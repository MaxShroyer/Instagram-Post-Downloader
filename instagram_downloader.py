"""
Instagram Post Downloader
A GUI application for downloading Instagram posts using the instaloader library.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional
import instaloader
import os
import logging
from pathlib import Path
import configparser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_downloader.log'),
        logging.StreamHandler()
    ]
)

class TwoFactorDialog:
    """Dialog for handling 2FA authentication."""

    def __init__(self, parent: tk.Tk) -> None:
        self.result: Optional[str] = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Two Factor Authentication")

        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self._center_window(300, 150)

        self._create_widgets()

    def _center_window(self, width: int, height: int) -> None:
        """Center the dialog window on screen."""
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = int(screen_width / 2 - width / 2)
        y = int(screen_height / 2 - height / 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self) -> None:
        """Create and arrange dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Please enter the 2FA code").pack(pady=(0, 10))

        self.code_var = tk.StringVar()
        self.code_entry = ttk.Entry(
            main_frame,
            textvariable=self.code_var,
            width=10,
            justify='center'
        )
        self.code_entry.pack(pady=(0, 20))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(
            btn_frame,
            text="Submit",
            command=self.submit
        ).pack(side=tk.LEFT, padx=5, expand=True)

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel
        ).pack(side=tk.LEFT, padx=5, expand=True)

        self.code_entry.focus_set()
        self.dialog.bind('<Return>', lambda e: self.submit())
        self.dialog.bind('<Escape>', lambda e: self.cancel())

    def submit(self) -> None:
        """Handle submission of 2FA code."""
        self.result = self.code_var.get()
        self.dialog.destroy()

    def cancel(self) -> None:
        """Handle cancellation of 2FA entry."""
        self.dialog.destroy()


class InstagramDownloaderGUI:
    """Main application class for the Instagram Post Downloader."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Instagram Post Downloader")
        self.root.geometry("400x500")

        self.L: Optional[instaloader.Instaloader] = None
        self.download_thread: Optional[threading.Thread] = None
        self.cancel_download = False

        self._create_main_frame()
        self._create_widgets()
        self._load_config()

    def _create_main_frame(self) -> None:
        """Create the main application frame."""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def _create_widgets(self) -> None:
        """Create and arrange application widgets."""
        # Username field
        ttk.Label(
            self.main_frame,
            text="Your Instagram Username:"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)

        self.username = ttk.Entry(self.main_frame, width=40)
        self.username.grid(row=1, column=0, sticky=tk.W, pady=5)

        # Password field
        ttk.Label(
            self.main_frame,
            text="Your Instagram Password:"
        ).grid(row=2, column=0, sticky=tk.W, pady=5)

        self.password = ttk.Entry(self.main_frame, width=40, show="*")
        self.password.grid(row=3, column=0, sticky=tk.W, pady=5)

        # Save credentials checkbox
        self.save_credentials_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.main_frame,
            text="Remember credentials",
            variable=self.save_credentials_var
        ).grid(row=4, column=0, sticky=tk.W, pady=5)

        # Target username field
        ttk.Label(
            self.main_frame,
            text="Target Instagram Username:"
        ).grid(row=5, column=0, sticky=tk.W, pady=5)

        self.target_username = ttk.Entry(self.main_frame, width=40)
        self.target_username.grid(row=6, column=0, sticky=tk.W, pady=5)

        # Number of posts field
        ttk.Label(
            self.main_frame,
            text="Number of Posts (leave empty for all):"
        ).grid(row=7, column=0, sticky=tk.W, pady=5)

        self.num_posts = ttk.Entry(self.main_frame, width=10)
        self.num_posts.grid(row=8, column=0, sticky=tk.W, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=9, column=0, pady=20)

        self.download_btn = ttk.Button(
            button_frame,
            text="Download Posts",
            command=self.start_download
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_download_action,
            state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            length=300,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_bar.grid(row=10, column=0, pady=5)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.main_frame,
            textvariable=self.status_var
        )
        self.status_label.grid(row=11, column=0, pady=5)

    def _load_config(self) -> None:
        """Load saved configuration and credentials."""
        try:
            config = configparser.ConfigParser()
            if os.path.exists('config.ini'):
                config.read('config.ini')
                if 'Credentials' in config:
                    self.username.insert(0, config['Credentials'].get('username', ''))
                    self.password.insert(0, config['Credentials'].get('password', ''))
                    self.save_credentials_var.set(True)
        except Exception as e:
            logging.error(f"Error loading config: {str(e)}")

    def _save_config(self) -> None:
        """Save configuration and credentials if enabled."""
        try:
            config = configparser.ConfigParser()
            if self.save_credentials_var.get():
                config['Credentials'] = {
                    'username': self.username.get(),
                    'password': self.password.get()
                }
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            logging.error(f"Error saving config: {str(e)}")

    def get_2fa_code(self) -> Optional[str]:
        """Show 2FA dialog and return entered code."""
        dialog = TwoFactorDialog(self.root)
        self.root.wait_window(dialog.dialog)
        return dialog.result

    def update_status(self, message: str, progress: Optional[float] = None) -> None:
        """Update status message and progress bar."""
        self.status_var.set(message)
        if progress is not None:
            self.progress_var.set(progress)
        self.root.update_idletasks()

    def reset_gui(self) -> None:
        """Reset GUI to initial state."""
        self.download_btn['state'] = 'normal'
        self.cancel_btn['state'] = 'disabled'
        self.status_var.set("Ready")
        self.progress_var.set(0)
        self.L = None
        self.cancel_download = False

    def cancel_download_action(self) -> None:
        """Handle download cancellation."""
        self.cancel_download = True
        self.update_status("Cancelling download...")
        self.cancel_btn['state'] = 'disabled'

    def start_download(self) -> None:
        """Start the download process."""
        if not self._validate_inputs():
            return

        if not self._show_warning():
            return

        self._prepare_download()
        self.download_thread = threading.Thread(target=self.download_posts)
        self.download_thread.start()

    def _validate_inputs(self) -> bool:
        """Validate user inputs before starting download."""
        if not all([self.username.get(), self.password.get(), self.target_username.get()]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return False
        return True

    def _show_warning(self) -> bool:
        """Show warning message about account safety."""
        warning_message = """WARNING: Mass downloading of Instagram posts can potentially lead to:

1. Your account being temporarily blocked
2. Account suspension or permanent ban
3. IP address restrictions

It's recommended to:
• Use this tool responsibly
• Take breaks between large downloads
• Avoid downloading thousands of posts at once
• Consider using a dedicated account

Do you want to continue?"""

        return messagebox.askyesno(
            "Account Safety Warning",
            warning_message,
            icon='warning'
        )

    def _prepare_download(self) -> None:
        """Prepare GUI and filesystem for download."""
        self.download_btn['state'] = 'disabled'
        self.cancel_btn['state'] = 'normal'
        self.cancel_download = False
        self.update_status("Logging in...", 0)

        # Create download directory
        target_username = self.target_username.get()
        download_dir = Path(f"posts_{target_username}")
        try:
            download_dir.mkdir(exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not create download directory: {str(e)}")
            return

    def download_posts(self) -> None:
        """Handle the main download process."""
        try:
            if not self._login():
                return

            profile = instaloader.Profile.from_username(self.L.context, self.target_username.get())
            posts = profile.get_posts()

            # Get posts list
            posts_list = []
            self.update_status("Counting posts...", 10)
            for post in posts:
                if self.cancel_download:
                    raise CancelledError("Download cancelled by user")
                posts_list.append(post)

            total_posts = len(posts_list)
            num_posts_limit = self.num_posts.get()

            if num_posts_limit:
                try:
                    num_posts_limit = int(num_posts_limit)
                    if num_posts_limit > 0:
                        total_posts = min(total_posts, num_posts_limit)
                except ValueError:
                    logging.warning("Invalid number of posts specified, downloading all posts")

            download_dir = Path(f"{self.target_username.get()}_posts")

            for index, post in enumerate(posts_list[:total_posts]):
                if self.cancel_download:
                    raise CancelledError("Download cancelled by user")

                progress = (index + 1) / total_posts * 100
                self.update_status(f"Downloading post {index + 1} of {total_posts}", progress)

                try:
                    self.L.download_post(post, target=str(download_dir))
                except Exception as e:
                    if "comments" not in str(e).lower() and "json" not in str(e).lower():
                        logging.error(f"Error downloading post: {str(e)}")
                        self.update_status(f"Error downloading post: {str(e)}")
                    continue

            if self.cancel_download:
                self.update_status("Download cancelled!")
            else:
                self.update_status("Download completed!", 100)
                self._save_config()
                messagebox.showinfo(
                    "Success",
                    f"Successfully downloaded {total_posts} posts to {download_dir}"
                )

        except CancelledError as e:
            logging.info(str(e))
        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.reset_gui()

    def _login(self) -> bool:
        """Handle Instagram login process including 2FA if needed."""
        try:
            self.L = instaloader.Instaloader(
                download_pictures=True,
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
                post_metadata_txt_pattern='',
                quiet=True
            )

            self.L.login(self.username.get(), self.password.get())
            return True

        except instaloader.TwoFactorAuthRequiredException:
            self.update_status("2FA Required")
            code = self.get_2fa_code()
            if code:
                try:
                    self.L.two_factor_login(code)
                    return True
                except Exception as e:
                    logging.error(f"2FA error: {str(e)}")
                    messagebox.showerror("Error", f"Invalid 2FA code: {str(e)}")
            return False

        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            messagebox.showerror("Error", f"Login failed: {str(e)}")
            return False


class CancelledError(Exception):
    """Custom exception for handling user-initiated cancellation."""
    pass


def main():
    """Main entry point of the application."""
    try:
        root = tk.Tk()
        app = InstagramDownloaderGUI(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Application error: {str(e)}")
        messagebox.showerror("Critical Error", f"Application error: {str(e)}")


if __name__ == "__main__":
    main()