from pytube import YouTube
import subprocess
import os
import sys
import yt_dlp  # Alternative downloader

def download_youtube_audio_pytube(url, output_filename='output.mp3'):
    """
    Download audio using pytube (may have HTTP 400 issues)
    """
    try:
        # Try with different configurations
        configs = [
            {},  # Default
            {'use_oauth': False, 'allow_oauth_cache': False},  # Disable OAuth
        ]
        
        for config in configs:
            try:
                print(f"Trying pytube configuration: {config}")
                yt = YouTube(url, **config)
                print(f"Title: {yt.title}")
                
                audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                if not audio_stream:
                    continue
                    
                print(f"Selected stream: {audio_stream.mime_type}, {audio_stream.abr}")
                audio_file = audio_stream.download(filename='audio_temp')
                
                # Convert to MP3
                result = subprocess.run(
                    ['ffmpeg', '-i', audio_file, '-y', output_filename], 
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    os.remove(audio_file)
                    print(f"Successfully downloaded with pytube: {output_filename}")
                    return True
                    
            except Exception as e:
                print(f"Pytube config failed: {e}")
                continue
                
        return False
        
    except Exception as e:
        print(f"Pytube error: {e}")
        return False

def download_youtube_audio_ytdlp(url, output_filename='output.mp3'):
    """
    Download audio using yt-dlp (more reliable alternative)
    """
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_audio.%(ext)s',
            'noplaylist': True,
        }
        
        print("Downloading with yt-dlp...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get info first
            info = ydl.extract_info(url, download=False)
            print(f"Title: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration', 'Unknown')} seconds")
            
            # Download
            ydl.download([url])
        
        # Find the downloaded file
        temp_files = [f for f in os.listdir('.') if f.startswith('temp_audio.')]
        if not temp_files:
            print("No audio file found after download")
            return False
            
        temp_file = temp_files[0]
        print(f"Downloaded: {temp_file}")
        
        # Convert to MP3 if needed
        if not temp_file.endswith('.mp3'):
            print("Converting to MP3...")
            result = subprocess.run(
                ['ffmpeg', '-i', temp_file, '-y', output_filename],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                return False
                
            os.remove(temp_file)
        else:
            os.rename(temp_file, output_filename)
        
        print(f"Successfully downloaded with yt-dlp: {output_filename}")
        return True
        
    except Exception as e:
        print(f"yt-dlp error: {e}")
        return False

def download_youtube_audio(url, output_filename='output.mp3'):
    """
    Try multiple methods to download YouTube audio
    """
    print("Attempting to download YouTube audio...")
    
    # Method 1: Try yt-dlp first (more reliable)
    if download_youtube_audio_ytdlp(url, output_filename):
        return True
    
    print("\nyt-dlp failed, trying pytube...")
    
    # Method 2: Try pytube as fallback
    if download_youtube_audio_pytube(url, output_filename):
        return True
    
    print("\nBoth methods failed!")
    return False

def main():
    # Get URL from user
    yt_url = input("YouTube link: ").strip()
    
    if not yt_url:
        print("No URL provided!")
        return
        
    # Optional: custom output filename
    custom_filename = input("Output filename (press Enter for 'output.mp3'): ").strip()
    output_file = custom_filename if custom_filename else 'output.mp3'
    
    # Ensure .mp3 extension
    if not output_file.endswith('.mp3'):
        output_file += '.mp3'
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: FFmpeg not found. Please install FFmpeg first.")
        return
    
    # Check if yt-dlp is available, install if not
    try:
        import yt_dlp
    except ImportError:
        print("yt-dlp not found. Install with: pip install yt-dlp")
        print("Continuing with pytube only...")
    
    # Download and convert
    success = download_youtube_audio(yt_url, output_file)
    
    if success:
        print("Done!")
    else:
        print("Download failed!")

if __name__ == "__main__":
    main()