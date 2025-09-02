from flask import *
from pymongo import MongoClient,errors
from werkzeug.security import *
from werkzeug.utils import secure_filename
import re,os,phonenumbers,json,gridfs,random
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'supersecretkey'
client = MongoClient('mongodb://localhost:27017/')
db = client['fleet_db']
users_collection = db['users']
fleet_collection = db['fleets']
maintenance_collection = db["maintenance"]
fs = gridfs.GridFS(db)


required_fields = [
            "fleet_id",
            "registration_no",
            "availability",
            "vehicle_name",
            "vehicle_type",
            "registration_city"
        ]
vehicle_types=["Van",
               "GSM Pickup",
               "Bus",
               "MotorBike",
               "Station Wagon",
               "Pickup Truck"]


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    fleet_collection.create_index("fleet_id", unique=True)
    fleet_collection.create_index("registration_no", unique=True)
    fleet_collection.create_index("win_no",unique=True)
    fleet_collection.create_index("engine_no",unique=True)

    with open("fleet_data.json") as f:
        fleet_data = json.load(f)
    all_valid = True
    for row in fleet_data:
        for field in required_fields:
            if field not in row or str(row[field]).strip() == "":
                all_valid = False
                break
        if row.get("vehicle_type") not in vehicle_types:
            print(f"Invalid vehicle type found: {row.get('vehicle_type')}")
            all_valid = False
            break

    if all_valid:
        new_entries = []
        for row in fleet_data:
            if not fleet_collection.find_one({"registration_no": row["registration_no"]}):
                new_entries.append(row)

        if new_entries:
            try:
                fleet_collection.insert_many(new_entries)
                print(f"✅ Inserted {len(new_entries)} new entries.")
            except errors.BulkWriteError as e:
                print("Insertion failed due to duplicate fleet_id:", e.details)
        else:
            print("No new entries to insert (all duplicates).")
    else:
        print("Insertion was aborted: Validation failed (empty fields or invalid vehicle type).")

    if request.method == 'POST':
        image = request.files.get('vehicle_image')
        if image and image.filename:
            if image.content_type.startswith('image/'):
                image_id = fs.put(image, filename=image.filename, content_type=image.content_type)

                # Store image_id in each fleet record for testing purposes (append to all fleets)
                fleet_docs = fleet_collection.find({})
                for fleet in fleet_docs:
                    vehicle_images = fleet.get('vehicle_images', [])
                    vehicle_images.append(str(image_id))
                    fleet_collection.update_one(
                        {'_id': fleet['_id']},
                        {'$set': {'vehicle_images': vehicle_images}}
                    )

            else:
                flash("Only image files are allowed!")
        return redirect(url_for('dashboard'))

    fleets = list(fleet_collection.find({}, {"_id": 0}))
    return render_template("dashboard.html", fleets=fleets, vehicle_types=vehicle_types)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            return redirect(url_for('dashboard'))  # Replace with redirect to dashboard
        else:
            flash("Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        country_code = request.form['country_code']
        phone = request.form['phone']
        dob = request.form['dob']
        username = request.form['username']
        password = request.form['password']
        full_number = country_code + phone
        try:
            parsed_number = phonenumbers.parse(full_number)
            if not phonenumbers.is_possible_number(parsed_number) or not phonenumbers.is_valid_number(parsed_number):
                flash("Invalid phone number")
                return redirect(url_for('register'))
        except phonenumbers.NumberParseException:
            flash("Invalid phone number format")
            return redirect(url_for('register'))

        if users_collection.find_one({'username': username}):
            flash("Username already exists")
            return redirect(url_for('register'))

        if not re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password):
            flash("Password must be 8+ chars, with a letter, number, and symbol")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        users_collection.insert_one({
            'phone': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
            'dob': dob,
            'username': username,
            'password': hashed_pw
        })

        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/image/<image_id>')
def get_image(image_id):
    try:
        image_file = fs.get(ObjectId(image_id))
        return send_file(image_file, mimetype=image_file.content_type)
    except:
        return "Image not found", 404
@app.route('/upload_vehicle_image/<fleet_id>', methods=['POST'])
def upload_vehicle_image(fleet_id):
    file = request.files.get('vehicle_image')
    if file and file.filename and file.content_type.startswith('image/'):
        try:
            # Save image to GridFS
            image_id = fs.put(file, filename=secure_filename(file.filename), content_type=file.content_type)
            fleet = fleet_collection.find_one({"fleet_id": fleet_id})
            if fleet:
                vehicle_images = fleet.get('vehicle_images', [])
                vehicle_images.append(str(image_id))
                fleet_collection.update_one(
                    {"fleet_id": fleet_id},
                    {"$set": {"vehicle_images": vehicle_images}}
                )
                flash("Vehicle image uploaded successfully.")
            else:
                flash("Fleet not found.")
        except Exception as e:
            flash(f"Upload failed: {str(e)}")
    else:
        flash("Invalid image file.")

    return redirect(url_for('dashboard'))

@app.route('/upload_registration_image/<fleet_id>', methods=['POST'])
def upload_registration_image(fleet_id):
    file = request.files.get('registration_image')
    if file and file.filename and file.content_type.startswith('image/'):
        try:
            image_id = fs.put(file, filename=secure_filename(file.filename), content_type=file.content_type)
            fleet = fleet_collection.find_one({"fleet_id": fleet_id})
            if fleet:
                reg_images = fleet.get('registration_images', [])
                reg_images.append(str(image_id))
                fleet_collection.update_one(
                    {"fleet_id": fleet_id},
                    {"$set": {"registration_images": reg_images}}
                )
                flash("Registration image uploaded.")
        except Exception as e:
            flash(f"Error uploading: {str(e)}")
    else:
        flash("Invalid file.")
    return redirect(url_for('dashboard'))


@app.route('/edit/<fleet_id>', methods=['POST'])
def edit_fleet(fleet_id):

    updated_fields = {
        "registration_no": request.form.get("registration_no"),
        "availability": request.form.get("availability"),
        "vehicle_name": request.form.get("vehicle_name"),
        "vehicle_type": request.form.get("vehicle_type"),
        "registration_city": request.form.get("registration_city"),
        "asset_no": request.form.get("asset_no"),
        "win_no": request.form.get("win_no"),
        "plate_no": request.form.get("plate_no"),
        "fuel_type": request.form.get("fuel_type"),
        "driving_license_type": request.form.get("driving_license_type"),
        "engine_no": request.form.get("engine_no"),
        "salik_account_no": request.form.get("salik_account_no"),
        "salik_tag_no": request.form.get("salik_tag_no"),
        "purchase_date": request.form.get("purchase_date"),
        "purchase_amount": request.form.get("purchase_amount"),
        "registration_expiry": request.form.get("registration_expiry"),
        "fuel_tank_capacity": request.form.get("fuel_tank_capacity"),
        "no_of_tyres": request.form.get("no_of_tyres"),
        "tyre_size": request.form.get("tyre_size"),
        "manufacturer": request.form.get("manufacturer"),
        "insurance_expiry": request.form.get("insurance_expiry"),
    }

    updated_fields = {k: v for k, v in updated_fields.items() if v is not None and v.strip() != ""}

    for key in ["registration_no", "win_no", "engine_no"]:
        if key in updated_fields:
            existing = fleet_collection.find_one({key: updated_fields[key], "fleet_id": {"$ne": fleet_id}})
            if existing:
                flash(f"{key.replace('_', ' ').title()} must be unique!")
                return redirect(url_for("dashboard"))

    result = fleet_collection.update_one({"fleet_id": fleet_id}, {"$set": updated_fields})
    if result.modified_count > 0:
        flash("Fleet details updated successfully.")
    else:
        flash("No changes were made.")
    return redirect(url_for("dashboard"))
@app.route('/delete_image/<fleet_id>/<image_id>/<image_type>', methods=['POST'])
def delete_image(fleet_id, image_id, image_type):
    try:
        fs.delete(ObjectId(image_id))
    except:
        flash("Image not found in GridFS")

    if image_type == 'vehicle':
        field = 'vehicle_images'
    elif image_type == 'registration':
        field = 'registration_images'
    else:
        return "Invalid image type", 400
    fleet_collection.update_one(
        {"fleet_id": fleet_id},
        {"$pull": {field: image_id}}
    )
    flash("Image deleted successfully.")
    return redirect(url_for('dashboard'))

@app.route('/maintenance_list', methods=['GET'])
def maintenance_list():
    vehicles = list(fleet_collection.find())
    maintenance = []
    for mnt in maintenance_collection.find():
        mnt['_id'] = str(mnt['_id'])  # convert ObjectId to string
        maintenance.append(mnt)
    return render_template("maintenance_list.html", vehicles=vehicles, maintenance=maintenance)





@app.route('/edit_maintenance/<maintenance_id>', methods=['POST'])
def edit_maintenance(maintenance_id):
    try:
        # Get the updated data from the form
        updated_data = {
            "maintenance_type": request.form.get("maintenance_type"),
            "remarks": request.form.get("remarks"),
            "start_date": request.form.get("start_date"),
            "expected_end_date": request.form.get("expected_end_date"),
            "maintenance_status": request.form.get("maintenance_status"),
            "odometer": request.form.get("odometer")
        }

        # Remove empty values
        updated_data = {k: v for k, v in updated_data.items() if v is not None and v.strip() != ""}

        # Update the maintenance record
        result = maintenance_collection.update_one(
            {"_id": ObjectId(maintenance_id)},
            {"$set": updated_data}
        )

        if result.modified_count > 0:
            flash("Maintenance record updated successfully.")
        else:
            flash("No changes were made.")

    except Exception as e:
        flash(f"Error updating maintenance record: {str(e)}")

    return redirect(url_for('maintenance_list'))


@app.route('/delete_maintenance/<maintenance_id>', methods=['POST'])
def delete_maintenance(maintenance_id):
    try:
        result = maintenance_collection.delete_one({"_id": ObjectId(maintenance_id)})

        if result.deleted_count > 0:
            flash("Maintenance record deleted successfully.")
        else:
            flash("Maintenance record not found.")

    except Exception as e:
        flash(f"Error deleting maintenance record: {str(e)}")

    return redirect(url_for('maintenance_list'))


@app.route('/add_maintenance', methods=['POST'])
def add_maintenance():
    if request.method == 'POST':
        fleet_id = request.form.get('fleet_id')
        vehicle = fleet_collection.find_one({'fleet_id': fleet_id})

        if not vehicle:
            flash("Invalid Fleet ID: No matching vehicle found.")
            return redirect(url_for('add_maintenance'))

        # Check if this vehicle already has an active maintenance record
        existing_maintenance = maintenance_collection.find_one({
            'fleet_id': fleet_id,
            'maintenance_status': {'$in': ['Booked for Maintenance', 'Under Maintenance']}
        })

        if existing_maintenance:
            flash(
                "This vehicle already has an active maintenance record. Please complete or cancel the existing maintenance before adding a new one.")
            return redirect(url_for('add_maintenance'))

        maintenance_collection.create_index("job_no", unique=True)
        maintenance_collection.create_index("maintenance_no", unique=True)

        generate_maintenance_no = "MNT" + ''.join([str(random.randint(0, 9)) for _ in range(10)])
        generate_job_no = ''.join([str(random.randint(0, 9)) for _ in range(7)])

        maintenance_data = {
            "fleet_id": fleet_id,
            "vehicle_name": vehicle['vehicle_name'],
            "vehicle_type": vehicle['vehicle_type'],
            "registration_city": vehicle['registration_city'],
            "maintenance_type": request.form['maintenance_type'],
            "remarks": request.form['remarks'],
            "start_date": request.form['start_date'],
            "expected_end_date": request.form['expected_end_date'],
            "job_no": request.form.get('job_no') or generate_job_no,
            "maintenance_status": request.form['maintenance_status'],
            "odometer": request.form['odometer'],
            "region": vehicle['registration_city'],
            "maintenance_no": generate_maintenance_no
        }

        try:
            maintenance_collection.insert_one(maintenance_data)
            flash("Maintenance record added successfully.")
        except errors.DuplicateKeyError as e:
            flash("Error: Duplicate job number or maintenance number. Please try again.")
            return redirect(url_for('add_maintenance'))

        return redirect(url_for('maintenance_list'))

    # GET handler - show the form
    vehicles = list(fleet_collection.find())
    return render_template("maintenance_list.html", vehicles=vehicles)


if __name__ == '__main__':
    app.run(debug=True)

