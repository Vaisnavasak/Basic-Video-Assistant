import tkinter as tk
from tkinter import font, filedialog
import cv2
from PIL import Image, ImageTk
import speech_recognition as sr
import threading
import google.generativeai as genai
import pyttsx3

# ─────────────────────────────────────────
#  GEMINI SETUP
# ─────────────────────────────────────────
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")

# ─────────────────────────────────────────
#  MAIN WINDOW SETUP
# ─────────────────────────────────────────
root = tk.Tk()
root.title("🎙️ Video AI Assistant")
root.geometry("1100x750")
root.configure(bg="#0f0f1a")
root.resizable(False, False)

# ─────────────────────────────────────────
#  FONTS
# ─────────────────────────────────────────
label_font    = tk.font.Font(family="Helvetica", size=12, weight="bold")
status_font   = tk.font.Font(family="Helvetica", size=10)
header_font   = tk.font.Font(family="Helvetica", size=20, weight="bold")
question_font = tk.font.Font(family="Helvetica", size=11)
btn_font      = tk.font.Font(family="Helvetica", size=10, weight="bold")

# ─────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────
header_frame = tk.Frame(root, bg="#0f0f1a", pady=10)
header_frame.pack(fill="x")

tk.Label(header_frame, text="🎙️  Video AI Assistant", font=header_font, bg="#0f0f1a", fg="#00d4ff").pack()
tk.Label(header_frame, text="Ask a question → AI answers → Video plays", font=status_font, bg="#0f0f1a", fg="#888888").pack()

tk.Frame(root, bg="#00d4ff", height=2).pack(fill="x", padx=20)

# ─────────────────────────────────────────
#  MAIN CONTENT AREA
# ─────────────────────────────────────────
content_frame = tk.Frame(root, bg="#0f0f1a", pady=15)
content_frame.pack(fill="both", expand=True, padx=20)

# ── LEFT PANEL: My Camera ───────────────
left_panel = tk.Frame(content_frame, bg="#1a1a2e", bd=2, relief="groove", width=500, height=420)
left_panel.pack(side="left", padx=(0, 10))
left_panel.pack_propagate(False)

tk.Label(left_panel, text="📷  MY CAMERA", font=label_font, bg="#1a1a2e", fg="#00d4ff", pady=10).pack()

camera_label = tk.Label(left_panel, bg="#0d0d1f")
camera_label.pack(padx=20, pady=(0, 10))

tk.Label(left_panel, text="🟢  Camera: Running", font=status_font, bg="#1a1a2e", fg="#00ff88").pack(pady=5)

# ── RIGHT PANEL: Video Player ────────────
right_panel = tk.Frame(content_frame, bg="#1a1a2e", bd=2, relief="groove", width=500, height=420)
right_panel.pack(side="right", padx=(10, 0))
right_panel.pack_propagate(False)

tk.Label(right_panel, text="🎬  VIDEO PLAYER", font=label_font, bg="#1a1a2e", fg="#ff6b35", pady=10).pack()

video_label = tk.Label(right_panel, bg="#0d0d1f")
video_label.pack(padx=20, pady=(0, 10))

right_status = tk.Label(right_panel, text="⏸️  Video: Paused", font=status_font, bg="#1a1a2e", fg="#ffaa00")
right_status.pack(pady=5)

# ─────────────────────────────────────────
#  QUESTION & ANSWER AREA
# ─────────────────────────────────────────
tk.Frame(root, bg="#333355", height=1).pack(fill="x", padx=20)

qa_frame = tk.Frame(root, bg="#0f0f1a", pady=8)
qa_frame.pack(fill="x", padx=20)

q_row = tk.Frame(qa_frame, bg="#0f0f1a")
q_row.pack(fill="x", pady=(0, 4))
tk.Label(q_row, text="🎙️ You:", font=status_font, bg="#0f0f1a", fg="#888888", width=6).pack(side="left")
question_label = tk.Label(q_row, text="— nothing yet —", font=question_font, bg="#0f0f1a", fg="#00d4ff", wraplength=920, justify="left")
question_label.pack(side="left", padx=10)

a_row = tk.Frame(qa_frame, bg="#0f0f1a")
a_row.pack(fill="x")
tk.Label(a_row, text="🤖 AI:", font=status_font, bg="#0f0f1a", fg="#888888", width=6).pack(side="left")
answer_label = tk.Label(a_row, text="— waiting for question —", font=question_font, bg="#0f0f1a", fg="#00ff88", wraplength=920, justify="left")
answer_label.pack(side="left", padx=10)

# ─────────────────────────────────────────
#  BOTTOM CONTROLS
# ─────────────────────────────────────────
tk.Frame(root, bg="#333355", height=1).pack(fill="x", padx=20)

bottom_frame = tk.Frame(root, bg="#0f0f1a", pady=15)
bottom_frame.pack(fill="x", padx=20)

ask_btn = tk.Button(
    bottom_frame,
    text="🎙️  Ask Question",
    font=label_font,
    bg="#00d4ff",
    fg="#0f0f1a",
    padx=20,
    pady=10,
    relief="flat",
    cursor="hand2",
    activebackground="#00aacc"
)
ask_btn.pack(side="left", padx=(0, 10))

import_btn = tk.Button(
    bottom_frame,
    text="📂  Import Video",
    font=btn_font,
    bg="#ff6b35",
    fg="#ffffff",
    padx=15,
    pady=10,
    relief="flat",
    cursor="hand2",
    activebackground="#cc4400"
)
import_btn.pack(side="left", padx=(0, 20))

status_bar = tk.Label(
    bottom_frame,
    text="🟡  Click 'Ask Question' to begin...",
    font=status_font,
    bg="#0f0f1a",
    fg="#aaaaaa"
)
status_bar.pack(side="left")

tk.Label(bottom_frame, text="✅  Complete!", font=status_font, bg="#0f0f1a", fg="#00d4ff").pack(side="right")

# ─────────────────────────────────────────
#  WEBCAM
# ─────────────────────────────────────────
cap = cv2.VideoCapture(0)

def show_camera():
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (460, 310))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)
    camera_label.after(10, show_camera)

show_camera()

# ─────────────────────────────────────────
#  VIDEO PLAYER
# ─────────────────────────────────────────
video_cap = cv2.VideoCapture("sample.mp4")
is_playing = False

def load_first_frame():
    ret, frame = video_cap.read()
    if ret:
        frame = cv2.resize(frame, (460, 310))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
        video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

def play_video():
    if is_playing:
        ret, frame = video_cap.read()
        if ret:
            frame = cv2.resize(frame, (460, 310))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)
            video_label.after(30, play_video)
        else:
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

def start_video():
    global is_playing
    # Restart from the beginning every time a new question is asked
    video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    is_playing = True
    right_status.config(text="▶️  Video: Playing", fg="#00ff88")
    play_video()

def stop_video():
    global is_playing
    is_playing = False
    right_status.config(text="⏸️  Video: Paused", fg="#ffaa00")

load_first_frame()

# ─────────────────────────────────────────
#  IMPORT VIDEO FUNCTION
# ─────────────────────────────────────────
def import_video():
    global video_cap
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")]
    )
    if file_path:
        stop_video()
        video_cap.release()
        video_cap = cv2.VideoCapture(file_path)
        load_first_frame()
        status_bar.config(text=f"✅  Video loaded: {file_path.split('/')[-1]}", fg="#00ff88")

import_btn.config(command=import_video)

# ─────────────────────────────────────────
#  AI ANSWER FUNCTION
# ─────────────────────────────────────────
def get_ai_answer(question):
    try:
        prompt = f"Answer this question clearly and concisely in 2-3 sentences: {question}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error getting answer: {str(e)}"

# ─────────────────────────────────────────
#  SPEAK + SYNC VIDEO
#  FIX: create a fresh pyttsx3 engine every call.
#  Reusing one global engine across multiple runAndWait()
#  calls is a well-known pyttsx3 bug — it works the first
#  time, then silently fails / returns instantly afterward,
#  which is why the video only "played" on question 1.
# ─────────────────────────────────────────
def speak_and_play(text):
    root.after(0, start_video)

    try:
        local_engine = pyttsx3.init()
        local_engine.setProperty("rate", 170)
        local_engine.setProperty("volume", 1.0)
        local_engine.say(text)
        local_engine.runAndWait()
        local_engine.stop()
        del local_engine
    except Exception as e:
        print(f"TTS error: {e}")

    root.after(0, stop_video)
    root.after(0, lambda: status_bar.config(
        text="✅  Done! Ask another question anytime.",
        fg="#00ff88"
    ))
    root.after(0, lambda: ask_btn.config(
        state="normal",
        text="🎙️  Ask Question"
    ))

# ─────────────────────────────────────────
#  VOICE INPUT + AI + SPEAK + VIDEO SYNC
# ─────────────────────────────────────────
recognizer = sr.Recognizer()

def listen_and_answer():
    ask_btn.config(state="disabled", text="⏳  Listening...")
    status_bar.config(text="🔴  Listening... Speak now!", fg="#ff4444")
    answer_label.config(text="— waiting for question —")
    root.update()

    def process():
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            question_text = recognizer.recognize_google(audio)
            root.after(0, lambda: question_label.config(text=question_text))
            root.after(0, lambda: status_bar.config(
                text="🤖  Getting Gemini answer...", fg="#ffaa00"))

            answer_text = get_ai_answer(question_text)
            root.after(0, lambda: answer_label.config(text=answer_text))
            root.after(0, lambda: status_bar.config(
                text="🔊  AI speaking + Video playing...", fg="#00d4ff"))

            threading.Thread(target=speak_and_play, args=(answer_text,), daemon=True).start()

        except sr.WaitTimeoutError:
            root.after(0, lambda: status_bar.config(text="⚠️  No speech detected. Try again!", fg="#ffaa00"))
            root.after(0, lambda: ask_btn.config(state="normal", text="🎙️  Ask Question"))
        except sr.UnknownValueError:
            root.after(0, lambda: status_bar.config(text="⚠️  Could not understand. Try again!", fg="#ffaa00"))
            root.after(0, lambda: ask_btn.config(state="normal", text="🎙️  Ask Question"))
        except Exception as e:
            root.after(0, lambda: status_bar.config(text=f"❌  Error: {str(e)}", fg="#ff4444"))
            root.after(0, lambda: ask_btn.config(state="normal", text="🎙️  Ask Question"))

    threading.Thread(target=process, daemon=True).start()

ask_btn.config(command=listen_and_answer)

# ─────────────────────────────────────────
#  CLOSE CLEANLY
# ─────────────────────────────────────────
def on_close():
    stop_video()
    cap.release()
    video_cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────
root.mainloop()