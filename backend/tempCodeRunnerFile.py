import uuid
from flask import Flask, flash, redirect, request, jsonify, render_template, session, url_for
from flask_session import Session
import os
import pandas as pd
from werkzeug.utils import secure_filename
import mysql.connector
from ai_module import process_video_and_attendance
import sys
sys.stdout.reconfigure(encoding='utf-8')
# Flask setup
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static', static_url_path='')

# đường dẫn UPLOAD_FOLDER
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/uploads')

ALLOWED_EXTENSIONS = {'mp4', 'jpg', 'jpeg', 'png', 'xls', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cấu hình Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SECRET_KEY'] = 'supersecretkey'
Session(app)

# MySQL setup
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'attendance_system'
}

# Helper function to validate file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'role' in session and session['role'] == 'teacher':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        class_id = request.form.get('class_id')

        if file.filename == '' or not class_id:
            return jsonify({'error': 'No selected file or class ID'}), 400

        if file and allowed_file(file.filename):
            try:
                # Tạo thư mục con theo class ID
                class_folder = os.path.join(app.config['UPLOAD_FOLDER'], class_id)
                os.makedirs(class_folder, exist_ok=True)

                # Tạo tên file ngẫu nhiên
                filename = secure_filename(file.filename)
                filepath = os.path.join(class_folder, filename)

                # Lưu file
                file.save(filepath)

                # Trả về thông báo upload video thành công
                return jsonify({'message': 'Video uploaded successfully!'}), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        return jsonify({'error': 'Invalid file type'}), 400

    return jsonify({'error': 'Unauthorized access'}), 403

@app.route('/process_attendance', methods=['POST'])
def process_attendance():
    if 'role' in session and session['role'] == 'teacher':
        class_id = request.form.get('class_id')

        if not class_id:
            flash('Class ID not found', 'danger')
            return redirect(url_for('teacher_dashboard'))

        video_folder = os.path.join(app.config['UPLOAD_FOLDER'], class_id)
        print(f"Video folder path: {video_folder}")
        try:
            video_files = [f for f in os.listdir(video_folder) if os.path.isfile(os.path.join(video_folder, f)) and allowed_file(f)]
            if not video_files:
                flash(f'No video found for class ID: {class_id}', 'danger')
                return redirect(url_for('teacher_dashboard'))

            video_path = os.path.join(video_folder, video_files[0])
            print(f"Video path: {video_path}")

            attendance_result = process_video_and_attendance(video_path, class_id, app.root_path)
            print(f"Attendance result: {attendance_result}")

            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT student_id FROM students WHERE class_id = %s", (class_id,))
            students_in_class = [student['student_id'] for student in cursor.fetchall()]

            present_students = []
            absent_students = []
            for student_id in students_in_class:
                if student_id in attendance_result:
                    status = 'present'
                else:
                    status = 'absent'

                cursor.execute("SELECT * FROM attendance WHERE class_id = %s AND student_id = %s AND date = CURDATE()", (class_id, student_id))
                existing_record = cursor.fetchone()

                if existing_record:
                    cursor.execute("UPDATE attendance SET status = %s WHERE class_id = %s AND student_id = %s AND date = CURDATE()", (status, class_id, student_id))
                else:
                    cursor.execute("INSERT INTO attendance (class_id, student_id, date, status) VALUES (%s, %s, CURDATE(), %s)", (class_id, student_id, status))

                if status == 'present':
                    if student_id not in present_students:
                        present_students.append(student_id)
                else:
                    if student_id in present_students:
                        status = 'present'
                        cursor.execute("UPDATE attendance SET status = %s WHERE class_id = %s AND student_id = %s AND date = CURDATE()", (status, class_id, student_id))
                    else:
                        absent_students.append(student_id)

            connection.commit()
        except Exception as e:
            flash(f'Error processing attendance: {e}', 'danger')
            return redirect(url_for('teacher_dashboard'))

            # Tạo DataFrame và lưu vào file Excel
        print(present_students)

    return jsonify({'error': 'Unauthorized access'}), 403
        
        
# Route: Register a student
@app.route('/register_student', methods=['POST'])
def register_student():
    try:
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        class_id = request.form.get('class_id')
        
        # Kiểm tra xem có file ảnh được upload không
        if 'face_image' not in request.files:
            return jsonify({'error': 'No face image uploaded'}), 400

        face_image_file = request.files['face_image']

        # Kiểm tra xem người dùng có chọn file không
        if face_image_file.filename == '':
            return jsonify({'error': 'No face image selected'}), 400
        
        # Kiểm tra định dạng file
        if not allowed_file(face_image_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Tạo tên file ngẫu nhiên và an toàn
        filename = str(uuid.uuid4()) + "_" + secure_filename(face_image_file.filename)
        
        # Tạo đường dẫn lưu file
        face_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'faces', filename)
        
        #Tạo đường dẫn đầy đủ đến thư mục
        os.makedirs(os.path.dirname(face_image_path), exist_ok=True)

        # Lưu file ảnh
        face_image_file.save(face_image_path)

        # Lưu thông tin sinh viên và đường dẫn ảnh vào cơ sở dữ liệu
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        sql = "INSERT INTO students (name, student_id, class_id, face_image) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, student_id, class_id,  'faces/' + filename)) # Lưu đường dẫn tương đối
        connection.commit()

        return jsonify({'message': 'Student registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            sql = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, password, role))
            connection.commit()

            flash("User registered successfully!", "success")
            return redirect(url_for('index'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
            return redirect(url_for('register'))
        finally:
            cursor.close()
            connection.close()
    return render_template('register.html')

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']

                # Lấy student_id từ bảng students dựa vào user_id
                cursor.execute("SELECT student_id FROM students WHERE name = %s", (username,))
                student = cursor.fetchone()
                if student:
                    session['student_id'] = student['student_id']
                else:
                    session['student_id'] = None

                if user['role'] == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                elif user['role'] == 'student':
                    return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')

# Route: Teacher Dashboard
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'role' in session and session['role'] == 'teacher':
        return render_template('teacher.html', username=session['username'])
    flash('Unauthorized access', 'danger')
    return redirect(url_for('login'))

# Route: Student Dashboard
@app.route('/student_dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        return render_template('student.html', username=session['username'])
    flash('Unauthorized access', 'danger')
    return redirect(url_for('login'))

# Route: Fetch attendance
@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    class_id = request.args.get('class_id')

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        sql = "SELECT * FROM attendance WHERE class_id = %s"
        cursor.execute(sql, (class_id,))
        records = cursor.fetchall()

        return jsonify({'attendance': records}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/create_class', methods=['POST'])
def create_class():
    if 'role' in session and session['role'] == 'teacher':
        class_id = request.form.get('class_id')
        class_name = request.form.get('class_name')
        class_password = request.form.get('class_password')
        teacher_id = session['user_id']

        if not (class_id and class_name and class_password):
            flash('All fields are required!', 'danger')
            return redirect(url_for('teacher_dashboard'))

        try:
            # Kết nối cơ sở dữ liệu
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Kiểm tra xem class_id đã tồn tại hay chưa
            cursor.execute("SELECT * FROM classes WHERE id = %s", (class_id,))
            if cursor.fetchone():
                flash('Class ID already exists!', 'danger')
                return redirect(url_for('teacher_dashboard'))

            # Lưu lớp học vào cơ sở dữ liệu
            sql = "INSERT INTO classes (id, class_name, class_password, teacher_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (class_id, class_name, class_password, teacher_id))
            connection.commit()

            flash('Class created successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('teacher_dashboard'))

    flash('Unauthorized access', 'danger')
    return redirect(url_for('login'))
    
# Route: Home
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_student_list', methods=['POST'])
def upload_student_list():
    if 'role' in session and session['role'] == 'teacher':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('teacher_dashboard'))

        file = request.files['file']
        class_id = request.form.get('class_id')

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('teacher_dashboard'))

        if file and allowed_file(file.filename):
            connection = None
            try:
                # Đọc file excel bằng pandas
                df = pd.read_excel(file)

                # Kiểm tra các cột cần thiết
                if not {'student_id', 'name'}.issubset(df.columns):
                    flash('Invalid excel file format', 'danger')
                    return redirect(url_for('teacher_dashboard'))

                # Kết nối cơ sở dữ liệu
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()

                # Thêm sinh viên vào cơ sở dữ liệu
                for index, row in df.iterrows():
                    student_id = row['student_id']
                    name = row['name']
                    
                    # Kiểm tra xem sinh viên đã tồn tại hay chưa dựa vào student_id
                    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
                    existing_student = cursor.fetchone()

                    if existing_student:
                        # Nếu sinh viên đã tồn tại, cập nhật thông tin sinh viên
                        update_sql = "UPDATE students SET name = %s, class_id = %s WHERE student_id = %s"
                        cursor.execute(update_sql, (name, class_id, student_id))
                    else:
                        # Nếu sinh viên chưa tồn tại, thêm mới sinh viên
                        sql = "INSERT INTO students (student_id, name, class_id) VALUES (%s, %s, %s)"
                        cursor.execute(sql, (student_id, name, class_id))

                connection.commit()
                flash('Student list uploaded successfully', 'success')

            except Exception as e:
                flash(f'Error: {e}', 'danger')
            finally:
                if connection and connection.is_connected():
                    cursor.close()
                    connection.close()

            return redirect(url_for('teacher_dashboard'))

        else:
            flash('Invalid file type', 'danger')
            return redirect(url_for('teacher_dashboard'))

    flash('Unauthorized access', 'danger')
    return redirect(url_for('login'))

# Route: Get students by class ID
@app.route('/get_students/<class_id>')
def get_students(class_id):
    if 'role' in session and session['role'] == 'teacher':
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT student_id, name FROM students WHERE class_id = %s", (class_id,))
            students = cursor.fetchall()
            return jsonify(students)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({'error': 'Unauthorized'}), 403

@app.route('/remove_student/<student_id>', methods=['DELETE'])
def remove_student(student_id):
    if 'role' in session and session['role'] == 'teacher':
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            connection.commit()
            return jsonify({'message': 'Student removed successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({'error': 'Unauthorized'}), 403

# Các chức năng của students
# Route: Join a class
@app.route('/join_class', methods=['POST'])
def join_class():
    if 'role' in session and session['role'] == 'student':
        data = request.get_json()
        class_id = data.get('class_id')
        class_password = data.get('class_password')
        student_id = session.get('student_id')

        if not class_id or not class_password:
            return jsonify({'error': 'Class ID and password are required'}), 400

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)

            # Kiểm tra thông tin lớp học
            cursor.execute("SELECT * FROM classes WHERE id = %s AND class_password = %s", (class_id, class_password))
            class_info = cursor.fetchone()

            if class_info:
                # Kiểm tra xem sinh viên đã tham gia lớp này chưa
                cursor.execute("SELECT * FROM students WHERE student_id = %s AND class_id = %s", (student_id, class_id))
                existing_student = cursor.fetchone()

                if existing_student:
                    return jsonify({'error': 'Student already in this class'}), 400
                else:
                    # Thêm sinh viên vào lớp
                    # Lấy thông tin sinh viên
                    cursor.execute("SELECT username FROM users WHERE id = %s", (session.get('user_id'),))
                    student_info = cursor.fetchone()
                    student_name = student_info['username'] if student_info else None

                    # Thêm sinh viên vào bảng students với class_id
                    cursor.execute("UPDATE students SET class_id = %s, name = %s WHERE student_id = %s", (class_id, student_name, student_id))
                    connection.commit()
                    return jsonify({'message': 'Class joined successfully'}), 200
            else:
                return jsonify({'error': 'Invalid class ID or password'}), 400

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    return jsonify({'error': 'Unauthorized'}), 403

# Route cho sinh viên 
@app.route('/get_students_student/<class_id>', endpoint='get_students_student')
def get_students_student(class_id):
    if 'role' in session and session['role'] == 'student':
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT student_id, name FROM students WHERE class_id = %s", (class_id,))
            students = cursor.fetchall()
            return jsonify(students)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({'error': 'Unauthorized'}), 403


@app.route('/upload_face', methods=['POST'])
def upload_face():
    if 'role' in session and session['role'] == 'student':
        if 'face_image' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('student_dashboard'))

        file = request.files['face_image']
        student_id_input = request.form.get('student_id_input')

        if file.filename == '' or not student_id_input:
            flash('No selected file or student ID', 'danger')
            return redirect(url_for('student_dashboard'))

        connection = None

        if file and allowed_file(file.filename):
            try:
                # Tạo thư mục con theo mã sinh viên
                student_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'faces', student_id_input)
                os.makedirs(student_folder, exist_ok=True)

                # Tạo tên file ngẫu nhiên
                filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
                filepath = os.path.join(student_folder, filename)

                # Lưu file
                file.save(filepath)

                # Cập nhật đường dẫn ảnh trong cơ sở dữ liệu
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                relative_filepath = os.path.join('faces', student_id_input, filename)

                # Kiểm tra xem student_id đã tồn tại trong bảng students chưa
                cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id_input,))
                student_record = cursor.fetchone()

                if student_record:
                    # Nếu student_id đã tồn tại, cập nhật face_image
                    cursor.execute("UPDATE students SET face_image = %s WHERE student_id = %s", (relative_filepath, student_id_input))
                else:
                    # Lấy thông tin user để cập nhật vào bảng students
                    user_id = session.get('user_id')
                    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
                    user_record = cursor.fetchone()
                    username = user_record[0] if user_record else ''

                    # Thêm mới sinh viên vào bảng students
                    cursor.execute("INSERT INTO students (student_id, name, face_image) VALUES (%s, %s, %s)", (student_id_input, username, relative_filepath))

                connection.commit()
                flash('Face image uploaded successfully', 'success')
                return redirect(url_for('student_dashboard'))

            except Exception as e:
                flash(f'Error: {e}', 'danger')
                print(f"Error during upload: {e}")
                return redirect(url_for('student_dashboard'))
            finally:
                if connection and connection.is_connected():
                    cursor.close()
                    connection.close()

        else:
            flash('Invalid file type', 'danger')
            return redirect(url_for('student_dashboard'))

    flash('Unauthorized access', 'danger')
    return redirect(url_for('login'))

@app.route('/get_session_data')
def get_session_data():
    if 'role' in session and session['role'] == 'student':
        return jsonify({
            'student_id': session.get('student_id'),
            'username': session.get('username'),
            'role': session.get('role')
        })
    else:
        return jsonify({'error':'unauthorized'}), 401


# Start the Flask app
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
