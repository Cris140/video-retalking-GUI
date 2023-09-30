import gradio as gr
import os
import shutil
import subprocess
import string
import random

# Global variable to store the previous video file name
previous_video_file_name = None

if os.path.isdir('checkpoints') == False:
    os.system("gdown --id 1gFCEoFgDQ8KL3yGOtAldXhuODtAvrl6G -O add.7z")
    os.system("pip install py7zr")
    os.system("py7zr x add.7z")
    shutil.move('./add ons/GFPGAN-engine', '../GFPGAN-engine')
    shutil.move('./add ons/checkpoints', './checkpoints')
else:
    print("Tudo já instalado, abrindo gradio...")

def generate_random_string(length=4):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def run_inference(uploaded_video, uploaded_audio, execute, enhance_with_gfpgan):
    global previous_video_file_name
    
    # Placeholder values
    command = ""
    video_path = ""
    audio_path = ""
    execution_result = "Command not executed."  # Default value assigned
    
    if previous_video_file_name:
        video_file_name = previous_video_file_name
    else:
        video_file_name = generate_random_string() + ".mp4"
        previous_video_file_name = video_file_name

    if not uploaded_video or not uploaded_audio:
        command = "Please upload both video and audio files."
    else:
        # Define paths where you want to save the uploaded files
        video_file_path = f"examples/face/{video_file_name}"
        audio_file_path = "examples/audio/audio.wav"
        output_file_path = "results/result.mp4"

        # Ensure directories exist
        for directory in ["examples/face", "examples/audio", "results"]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Save the uploaded files to the specified locations
        with open(video_file_path, 'wb') as video_out, open(uploaded_video.name, 'rb') as video_in:
            shutil.copyfileobj(video_in, video_out)
        video_path = video_file_path

        with open(audio_file_path, 'wb') as audio_out, open(uploaded_audio.name, 'rb') as audio_in:
            shutil.copyfileobj(audio_in, audio_out)
        audio_path = audio_file_path

        # Create the command string for inference
        command = f"python inference.py --face {video_file_path} --audio {audio_file_path} --outfile {output_file_path}"

        if execute:
            try:
                execution_result = subprocess.check_output(command, shell=True).decode("utf-8")
                video_path = output_file_path  # set the video_path to the processed video if the command is executed
                audio_path = None  # ensure the audio won't be shown in the GUI after processing

                # If the GFPGAN option is selected
                if enhance_with_gfpgan:
                    gfpgan_command = f"python C:/GFPGAN-engine/src/video_enhance2.py -i results/result.mp4 -o results/high.mp4"

                    subprocess.check_output(gfpgan_command, shell=True)
                    video_path = "results/high.mp4"
                
            except subprocess.CalledProcessError as e:
                execution_result = str(e)

            # Cleanup: Delete temporary video and audio files
            if os.path.exists(video_file_path):
                os.remove(video_file_path)
                previous_video_file_name = None  # Reset the video file name once it's removed
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)

    return command, video_path, audio_path, execution_result

# Gradio Interface
iface = gr.Interface(
    fn=run_inference,
    inputs=[
        gr.components.File(label="Upload Video", type="file"),
        gr.components.File(label="Upload Audio", type="file"),
        gr.components.Checkbox(label="Execute Command?"),
        gr.components.Checkbox(label="Enhance with GFPGAN?")
    ],
    outputs=[
        gr.components.Textbox(label="Generated Command"),
        gr.components.Video(label="Processed Video (or Uploaded Video if not processed)"),
        gr.components.Audio(label="Uploaded Audio"),
        gr.components.Textbox(label="Execution Result")
    ],
    title="Video-Retalking with GFPGAN Enhancement",
    description="GUI by Shmuel Ronen"
)

if __name__ == "__main__":
    iface.launch()
