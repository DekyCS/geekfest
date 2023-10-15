from flask import Flask, redirect, render_template, request, session, Response, jsonify
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
import face_recognition
from flask_session import Session
import os, sys
import cv2
import numpy as np
import math
from camera import VideoCamera
import time

app = Flask(__name__, static_url_path='/static', static_folder='static')
db = SQL("sqlite:///geekfest.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config["secret_key"] = os.urandom(100000000)

video_stream = VideoCamera()

@app.route("/", methods=["GET", "POST"])
def index():
    return redirect("/login")
        
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login5.html")
        
    else:
        
        username = request.form.get("username")
        password = request.form.get("password")
        userid = db.execute("SELECT userid FROM users WHERE username = %s", username)
        


        if not userid:
            print("did not found accout")
            return redirect('/login')
 
        else:
            print("made connections")
            correctPassword = db.execute("SELECT password FROM users where username = ?", username)
            print(correctPassword[0]['password'])
            if check_password_hash(correctPassword[0]['password'], password) or correctPassword[0]['password']:
                print("connected with the hash")
                return redirect("/done")
            else:
                print("failed to connect")
                return redirect("/login")
        


@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "GET":
        return render_template("register5.html")
        

    else:
        print("made a request to the /register page")
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm = request.form.get("password2")

        

        users = db.execute("SELECT * FROM users WHERE username = %s", (username,))

        if not users: # no users with the same username
            if password != password_confirm:
                return redirect("/register")
            else:
                print(generate_password_hash(password))
                db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, generate_password_hash(password))
                print("we have made a new user")
                return redirect("/login")
        else:
            return redirect("/register") # their existe alr a user with that username

@app.route("/bellxlogin", methods=["GET", "POST"])
def bellxlogin():

    if request.method == "GET":

        return render_template("login12.html")
        
    else:
        username = request.form.get("username")
        #password = request.form.get("password")
        userid = db.execute("SELECT userid FROM usersbellx WHERE username = %s", username)
        
        
        if not userid:
            print("dont existe a userid")
            return redirect('/login')
            
            
        else:
            print("made conntection")
            correctPassword = db.execute("SELECT password FROM usersbellx WHERE username = ?", username)
            if check_password_hash(correctPassword[0]['password'], password):
                print("connected")
                session["userid"] = userid[0]['userid']
                print(session["userid"])
                return redirect("/done")
            else:
                return redirect("/login")
        


@app.route("/bellxregister", methods=["GET", "POST"])
def bellxregister():
    
    if request.method == "GET":
        return render_template("register12.html")


    else:
        
        username = request.form.get("username")

        #password = request.form.get("password")
        #password_confirm = request.form.get("password2")

        
        db.execute("INSERT INTO usersbellx (username) VALUES (?)", username) 
        users = db.execute("SELECT * FROM usersbellx WHERE username = %s", (username))
        
        session["userid"] = users[0]['userid']

        newfilename = "./static/faces/" + str(session["userid"]) + ".jpg"
        os.rename("./static/faces/tobechanged.jpg", newfilename)

        """"
        if not users: # no users with the same username
            if password != password_confirm:
                return redirect("/register")
            else:
                db.execute("INSERT INTO usersbellx (username, password) VALUES (?, ?)", username, generate_password_hash(password))
                userid = db.execute("SELECT userid FROM usersbellx WHERE username = %s", username)
                session["userid"] = userid[0]['userid']

                print("we have made a new user")
                print(session["userid"])
                return redirect("/login")
        else:
            return redirect("/register") # their existe alr a user with that username
        """
        return redirect("/done")
        
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route("/done", methods=["GET", "POST"])
def done():
    return render_template("done.html")

@app.route("/faceid", methods=["GET", "POST"])
def faceid():
    fr = FaceRecognition()
    fr.run_recognition()
    return "hello"
        
@app.route('/video_feed')
def video_feed():
     return Response(gen(video_stream),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/take_picture", methods=["GET", "POST"])
def take_picture():
    if request.method == "POST":

        cam = cv2.VideoCapture(0)

        #cv2.namedWindow("test")


        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
        #cv2.imshow("test", frame)

        img_name = f"./static/faces/tobechanged.jpg"
        cv2.imwrite(img_name, frame)
        #print("{} written!".format(img_name))

        cam.release()

        cv2.destroyAllWindows()

        return redirect('/bellxlogin')
    
@app.route("/scan_face", methods=["GET", "POST"])
def scan_face():
    if request.method == "POST":

        check = request.form.get("check")
        check2 = request.form.get("check2")

        if check:
            username = request.form.get("username")
            password = request.form.get("password")
            password_confirm = request.form.get("password_confirm")

            if not username:
                return jsonify({"message": "no_username"})

            users = db.execute("SELECT * FROM users WHERE username = %s", (username))

            if not users: # no users with the same username
                if password != password_confirm:
                    return redirect("/register")
                else:

                    userid = session["userid"]


                    for i in range(3):
                        fr = FaceRecognition()
                        result = fr.run_recognition()

                        confidence = result[1][:2]     

                        if (result[0][:-4] == str(userid) and int(confidence) > 90):
                            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, generate_password_hash(password))
                            db.execute("INSERT INTO passwords (username, password, userid) VALUES (?, ?, ?)", username, password, userid)
                            return jsonify({"message": "succesful"})
                        else:
                            return jsonify({"message": "no_faceid"})
            else:
                return jsonify({"message": "username_used"})
        elif check2:

            print("i am here")
            userid = session["userid"]

            print("Session:" + str(userid))
            for i in range(3):
                fr = FaceRecognition()
                result = fr.run_recognition()

                confidence = result[1][:2]


                if (result[0][:-4] == str(userid) and int(confidence) > 90):
                    searchlogin = db.execute("SELECT * FROM passwords WHERE userid = ?", userid)
                    print(searchlogin[0])
                    return jsonify({"username": searchlogin[0]["username"], "password": searchlogin[0]["password"]})
                    
                else:
                    return jsonify({"message": "no_faceid"})
                    
        else:
            username = request.form.get("username")

            searchUsername = db.execute("SELECT * FROM usersbellx WHERE username = ?", username)

            if searchUsername:

                userid = searchUsername[0]["userid"]
                print(str(userid))


                for i in range(3):
                    fr = FaceRecognition()
                    result = fr.run_recognition()

                    confidence = result[1][:2]


                    if (result[0][:-4] == str(userid) and int(confidence) > 90):
                        session["userid"] = userid
                        return jsonify({"message": "succesful"})
                        
                    else:
                        return jsonify({"message": "no_faceid"})
            else:
                return jsonify({"message": "no_username"})

    return redirect('/login')


#FaceID Code
#Calculate validation percentage
def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linerar_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linerar_val * 100, 2)) + "%"
    else:
        value = (linerar_val + ((1.0 - linerar_val) * math.pow((linerar_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + "%"

class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_name = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True

    def __init__(self):
        self.encode_faces()
    #encode faces

    def encode_faces(self):
        print(os.listdir('./static/faces'))

        for image in os.listdir('./static/faces'):
            face_image = face_recognition.load_image_file(f'./static/faces/{image}')
            face_encoding = face_recognition.face_encodings(face_image)[0]
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)
        #print(self.known_face_names)

    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit("Video source not found...")

        start_time = time.time()

        while ((time.time() - start_time) < 1):
            ret, frame = video_capture.read()

            if self.process_current_frame:
                small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]

                #Find all faces in the current form
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = 'Unknown'
                    confidence = 'Unknown'

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])

                    self.face_names.append(f'{name} ({confidence})')

                    #print(confidence)
                    if name and confidence:
                        return name, confidence

            self.process_current_frame = not self.process_current_frame

            
            # Display annotations

            """
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
            """
            #cv2.imshow('Face Recognition', frame)

            #name = self.known_face_names[best_match_index]

            #print(name)
            #print(confidence)

            time.sleep(1)

        



        
        video_capture.release()
        cv2.destroyAllWindows()


        

if __name__ == '__main__':
    app.run(debug=True)


             
