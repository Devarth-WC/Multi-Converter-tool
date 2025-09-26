import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
import ffmpeg
import shutil

class AudioConverter:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Check if ffmpeg is available
        self.ffmpeg_available = which("ffmpeg") is not None
        if not self.ffmpeg_available:
            print("Warning: ffmpeg not found. Some audio conversions may not work.")
    
    def audio_to_text(self, audio_path, output_path):
        """Convert audio file to text using speech recognition"""
        try:
            # Convert to WAV if needed for speech recognition
            audio = AudioSegment.from_file(audio_path)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_wav_path = temp_wav.name
            
            # Export as WAV (speech_recognition works best with WAV)
            audio.export(temp_wav_path, format="wav")
            
            # Perform speech recognition
            with sr.AudioFile(temp_wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)
            
            # Recognize speech using Google's service
            try:
                text = self.recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                text = "Could not understand the audio content."
            except sr.RequestError as e:
                # Fallback to offline recognition if available
                try:
                    text = self.recognizer.recognize_sphinx(audio_data)
                except:
                    text = f"Speech recognition service error: {str(e)}"
            
            # Save text to file
            with open(output_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
            
            # Clean up temporary file
            os.unlink(temp_wav_path)
            
            return output_path
            
        except Exception as e:
            # Clean up temporary file if it exists
            if 'temp_wav_path' in locals() and os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)
            raise Exception(f"Audio to text conversion failed: {str(e)}")
    
    def convert_audio_format(self, input_path, output_path, target_format=None):
        """Convert audio file to different format"""
        try:
            if target_format is None:
                target_format = os.path.splitext(output_path)[1][1:]  # Get extension without dot
            
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Export in target format
            audio.export(output_path, format=target_format)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio format conversion failed: {str(e)}")
    
    def compress_audio(self, input_path, output_path, bitrate='64k'):
        """Compress audio file by reducing bitrate"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Export with lower bitrate
            audio.export(output_path, format="mp3", bitrate=bitrate)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio compression failed: {str(e)}")
    
    def extract_audio_from_video(self, video_path, output_path):
        """Extract audio from video file"""
        try:
            if not self.ffmpeg_available:
                raise Exception("ffmpeg is required for video to audio conversion")
            
            # Use ffmpeg to extract audio
            (
                ffmpeg
                .input(video_path)
                .output(output_path, acodec='libmp3lame', audio_bitrate='128k')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio extraction from video failed: {str(e)}")
    
    def merge_audio_files(self, audio_paths, output_path):
        """Merge multiple audio files into one"""
        try:
            if not audio_paths:
                raise Exception("No audio files provided for merging")
            
            # Load first audio file
            merged_audio = AudioSegment.from_file(audio_paths[0])
            
            # Add remaining audio files
            for audio_path in audio_paths[1:]:
                audio = AudioSegment.from_file(audio_path)
                merged_audio += audio
            
            # Export merged audio
            merged_audio.export(output_path, format="mp3")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio merging failed: {str(e)}")
    
    def trim_audio(self, input_path, output_path, start_time=0, end_time=None):
        """Trim audio file to specified duration"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Convert time to milliseconds
            start_ms = start_time * 1000
            end_ms = end_time * 1000 if end_time else len(audio)
            
            # Trim audio
            trimmed_audio = audio[start_ms:end_ms]
            
            # Export trimmed audio
            trimmed_audio.export(output_path, format="mp3")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio trimming failed: {str(e)}")
    
    def change_audio_speed(self, input_path, output_path, speed_factor=1.0):
        """Change audio playback speed"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Change speed (and pitch)
            if speed_factor > 1.0:
                # Speed up
                audio = audio.speedup(playback_speed=speed_factor)
            elif speed_factor < 1.0:
                # Slow down
                audio = audio.speedup(playback_speed=speed_factor)
            
            # Export modified audio
            audio.export(output_path, format="mp3")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio speed change failed: {str(e)}")
    
    def normalize_audio(self, input_path, output_path):
        """Normalize audio volume levels"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Normalize audio
            normalized_audio = audio.normalize()
            
            # Export normalized audio
            normalized_audio.export(output_path, format="mp3")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Audio normalization failed: {str(e)}")
    
    def get_audio_info(self, audio_path):
        """Get audio file information"""
        try:
            audio = AudioSegment.from_file(audio_path)
            
            return {
                'duration': len(audio) / 1000.0,  # Duration in seconds
                'channels': audio.channels,
                'sample_rate': audio.frame_rate,
                'sample_width': audio.sample_width,
                'frame_count': audio.frame_count(),
                'max_possible_amplitude': audio.max_possible_amplitude
            }
            
        except Exception as e:
            raise Exception(f"Failed to get audio info: {str(e)}")
    
    def add_silence(self, input_path, output_path, silence_duration=1.0, position='end'):
        """Add silence to audio file"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Create silence
            silence = AudioSegment.silent(duration=silence_duration * 1000)  # Convert to milliseconds
            
            # Add silence
            if position == 'start':
                modified_audio = silence + audio
            elif position == 'end':
                modified_audio = audio + silence
            else:  # 'both'
                modified_audio = silence + audio + silence
            
            # Export modified audio
            modified_audio.export(output_path, format="mp3")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Adding silence failed: {str(e)}")
