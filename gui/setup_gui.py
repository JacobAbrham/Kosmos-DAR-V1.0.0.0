#!/usr/bin/env python3
"""
KOSMOS Setup GUI - Windows Application
A graphical interface for setting up KOSMOS development environment
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import sys
import os
from pathlib import Path


class KosmosSetupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KOSMOS Development Environment Setup")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Set icon (if available)
        # self.root.iconbitmap("kosmos.ico")
        
        # Variables
        self.selected_option = tk.IntVar(value=1)
        self.setup_running = False
        
        # Create UI
        self.create_header()
        self.create_options_frame()
        self.create_details_frame()
        self.create_action_buttons()
        self.create_output_frame()
        self.create_status_bar()
        
    def create_header(self):
        """Create header with logo and title"""
        header_frame = tk.Frame(self.root, bg="#0066cc", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🚀 KOSMOS Development Environment Setup",
            font=("Arial", 18, "bold"),
            bg="#0066cc",
            fg="white"
        )
        title_label.pack(pady=20)
        
    def create_options_frame(self):
        """Create frame with environment options"""
        options_frame = tk.LabelFrame(
            self.root,
            text="Select Development Environment",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Option 1: Local Docker
        rb1 = tk.Radiobutton(
            options_frame,
            text="🐳 Local Docker Compose",
            variable=self.selected_option,
            value=1,
            font=("Arial", 11),
            command=self.update_details
        )
        rb1.pack(anchor=tk.W, pady=5)
        
        # Option 2: Codespaces
        rb2 = tk.Radiobutton(
            options_frame,
            text="☁️  GitHub Codespaces",
            variable=self.selected_option,
            value=2,
            font=("Arial", 11),
            command=self.update_details
        )
        rb2.pack(anchor=tk.W, pady=5)
        
        # Option 3: Remote Server
        rb3 = tk.Radiobutton(
            options_frame,
            text="🖥️  Remote Development Server",
            variable=self.selected_option,
            value=3,
            font=("Arial", 11),
            command=self.update_details
        )
        rb3.pack(anchor=tk.W, pady=5)
        
        # Option 4: Kubernetes
        rb4 = tk.Radiobutton(
            options_frame,
            text="☸️  Shared Kubernetes Cluster",
            variable=self.selected_option,
            value=4,
            font=("Arial", 11),
            command=self.update_details
        )
        rb4.pack(anchor=tk.W, pady=5)
        
        # Option 5: Gitpod
        rb5 = tk.Radiobutton(
            options_frame,
            text="🌐 Gitpod Cloud IDE",
            variable=self.selected_option,
            value=5,
            font=("Arial", 11),
            command=self.update_details
        )
        rb5.pack(anchor=tk.W, pady=5)
        
    def create_details_frame(self):
        """Create frame showing selected option details"""
        self.details_frame = tk.LabelFrame(
            self.root,
            text="Environment Details",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10
        )
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.details_text = tk.Text(
            self.details_frame,
            height=8,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        self.update_details()
        
    def create_action_buttons(self):
        """Create action buttons"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.setup_button = tk.Button(
            button_frame,
            text="▶ Start Setup",
            font=("Arial", 12, "bold"),
            bg="#28a745",
            fg="white",
            padx=30,
            pady=10,
            command=self.start_setup
        )
        self.setup_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = tk.Button(
            button_frame,
            text="✖ Cancel",
            font=("Arial", 12),
            bg="#dc3545",
            fg="white",
            padx=30,
            pady=10,
            command=self.cancel_setup,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        help_button = tk.Button(
            button_frame,
            text="❓ Help",
            font=("Arial", 12),
            bg="#17a2b8",
            fg="white",
            padx=30,
            pady=10,
            command=self.show_help
        )
        help_button.pack(side=tk.RIGHT, padx=5)
        
    def create_output_frame(self):
        """Create output log frame"""
        output_frame = tk.LabelFrame(
            self.root,
            text="Setup Progress",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=10,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_details(self):
        """Update details based on selected option"""
        option = self.selected_option.get()
        
        details = {
            1: {
                "title": "Local Docker Compose",
                "description": "Run everything on your local machine using Docker.\n\n",
                "requirements": "• Docker Desktop installed\n• 8GB RAM\n• 20GB disk space\n\n",
                "cost": "Cost: FREE\n\n",
                "best_for": "Best for: Individual developers, offline work",
                "skill": "Skill Level: ⭐ Beginner",
                "time": "Setup Time: 10-15 minutes"
            },
            2: {
                "title": "GitHub Codespaces",
                "description": "Cloud-based development environment from GitHub.\n\n",
                "requirements": "• GitHub account\n• Web browser\n\n",
                "cost": "Cost: Free tier (60 hrs/month), then $0.18/hr\n\n",
                "best_for": "Best for: Quick setup, any device",
                "skill": "Skill Level: ⭐ Beginner",
                "time": "Setup Time: 3-5 minutes"
            },
            3: {
                "title": "Remote Development Server",
                "description": "Connect to a shared development server via SSH.\n\n",
                "requirements": "• SSH access to server\n• Remote server with Docker\n• VS Code with Remote SSH\n\n",
                "cost": "Cost: Variable (server costs)\n\n",
                "best_for": "Best for: Team collaboration",
                "skill": "Skill Level: ⭐⭐ Intermediate",
                "time": "Setup Time: 15-20 minutes"
            },
            4: {
                "title": "Shared Kubernetes Cluster",
                "description": "Production-like environment with personal namespace.\n\n",
                "requirements": "• kubectl installed\n• Helm installed\n• K8s cluster access\n\n",
                "cost": "Cost: $50-200/month (shared)\n\n",
                "best_for": "Best for: Production-like development",
                "skill": "Skill Level: ⭐⭐⭐ Advanced",
                "time": "Setup Time: 20-30 minutes"
            },
            5: {
                "title": "Gitpod Cloud IDE",
                "description": "Browser-based IDE with automatic configuration.\n\n",
                "requirements": "• GitHub account\n• Web browser\n\n",
                "cost": "Cost: Free tier (50 hrs/month), then $0.36/hr\n\n",
                "best_for": "Best for: Quick demos, POCs",
                "skill": "Skill Level: ⭐ Beginner",
                "time": "Setup Time: 3-5 minutes"
            }
        }
        
        detail = details.get(option, details[1])
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        # Add content with formatting
        self.details_text.insert(tk.END, detail["description"])
        self.details_text.insert(tk.END, "Requirements:\n", "bold")
        self.details_text.insert(tk.END, detail["requirements"])
        self.details_text.insert(tk.END, detail["cost"])
        self.details_text.insert(tk.END, detail["best_for"] + "\n")
        self.details_text.insert(tk.END, detail["skill"] + "\n")
        self.details_text.insert(tk.END, detail["time"])
        
        self.details_text.config(state=tk.DISABLED)
        
    def log_output(self, message, color="white"):
        """Add message to output log"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update()
        
    def start_setup(self):
        """Start the setup process"""
        option = self.selected_option.get()
        
        # Show .env configuration dialog first
        if not self.configure_env_variables():
            return
        
        # Confirm
        option_names = {
            1: "Local Docker Compose",
            2: "GitHub Codespaces",
            3: "Remote Development Server",
            4: "Shared Kubernetes",
            5: "Gitpod Cloud IDE"
        }
        
        confirm = messagebox.askyesno(
            "Confirm Setup",
            f"Start setup for:\n{option_names[option]}\n\nThis may take 10-30 minutes.\nContinue?"
        )
        
        if not confirm:
            return
            
        # Disable setup button, enable cancel
        self.setup_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.setup_running = True
        
        # Clear output
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        # Run setup in thread
        thread = threading.Thread(target=self.run_setup, args=(option,))
        thread.daemon = True
        thread.start()
        
    def run_setup(self, option):
        """Run the actual setup script"""
        script_map = {
            1: "scripts/setup-local-docker.ps1",
            2: "scripts/setup-codespaces.ps1",
            3: "scripts/setup-remote-server.ps1",
            4: "scripts/setup-k8s-dev.ps1",
            5: "scripts/setup-gitpod.ps1"
        }
        
        script = script_map.get(option)
        
        if not script or not Path(script).exists():
            self.log_output(f"❌ Setup script not found: {script}")
            self.setup_complete(False)
            return
            
        self.log_output(f"▶ Starting setup...")
        self.log_output(f"▶ Running: {script}\n")
        self.update_status("Running setup...")
        
        try:
            # Run PowerShell script
            process = subprocess.Popen(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output in real-time
            for line in process.stdout:
                if not self.setup_running:
                    process.terminate()
                    break
                self.log_output(line.rstrip())
                
            # Wait for completion
            process.wait()
            
            if process.returncode == 0:
                self.log_output("\n✅ Setup completed successfully!")
                self.setup_complete(True)
            else:
                error = process.stderr.read()
                self.log_output(f"\n❌ Setup failed with error:\n{error}")
                self.setup_complete(False)
                
        except Exception as e:
            self.log_output(f"\n❌ Error running setup: {str(e)}")
            self.setup_complete(False)
            
    def setup_complete(self, success):
        """Handle setup completion"""
        self.setup_running = False
        self.setup_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        
        if success:
            self.update_status("Setup completed successfully!")
            messagebox.showinfo(
                "Setup Complete",
                "✅ Setup completed successfully!\n\n"
                "Check the output log for next steps."
            )
        else:
            self.update_status("Setup failed")
            messagebox.showerror(
                "Setup Failed",
                "❌ Setup encountered errors.\n\n"
                "Please check the output log and try again."
            )
            
    def cancel_setup(self):
        """Cancel running setup"""
        if messagebox.askyesno("Cancel Setup", "Are you sure you want to cancel?"):
            self.setup_running = False
            self.log_output("\n⚠️ Setup cancelled by user")
            self.update_status("Setup cancelled")
            self.setup_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            
    def configure_env_variables(self):
        """Show dialog to configure .env variables"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Environment Variables")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header = tk.Label(
            dialog,
            text="⚙️ Environment Configuration",
            font=("Arial", 14, "bold"),
            bg="#0066cc",
            fg="white",
            pady=15
        )
        header.pack(fill=tk.X)
        
        info = tk.Label(
            dialog,
            text="Configure your environment variables. Leave blank to use defaults.",
            font=("Arial", 10),
            pady=10
        )
        info.pack()
        
        # Scrollable frame for variables
        canvas = tk.Canvas(dialog)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Define environment variables with descriptions
        env_vars = [
            ("POSTGRES_DB", "kosmos", "PostgreSQL database name", True),
            ("POSTGRES_USER", "kosmos", "PostgreSQL username", True),
            ("POSTGRES_PASSWORD", "kosmos_dev_password", "PostgreSQL password", True),
            ("REDIS_PASSWORD", "redis_dev_password", "Redis password", True),
            ("MINIO_ROOT_USER", "minioadmin", "MinIO admin username", True),
            ("MINIO_ROOT_PASSWORD", "minioadmin123", "MinIO admin password", True),
            ("NATS_USER", "kosmos", "NATS username", True),
            ("NATS_PASSWORD", "nats_dev_password", "NATS password", True),
            ("GITHUB_TOKEN", "", "GitHub Personal Access Token (optional)", False),
            ("OPENAI_API_KEY", "", "OpenAI API Key (optional)", False),
            ("ANTHROPIC_API_KEY", "", "Anthropic API Key (optional)", False),
            ("SLACK_WEBHOOK_URL", "", "Slack webhook for notifications (optional)", False),
            ("ENVIRONMENT", "development", "Environment name", True),
            ("LOG_LEVEL", "INFO", "Logging level (DEBUG/INFO/WARNING/ERROR)", True),
        ]
        
        # Create entry fields
        self.env_entries = {}
        for i, (var_name, default, description, required) in enumerate(env_vars):
            frame = tk.Frame(scrollable_frame, pady=5, padx=10)
            frame.pack(fill=tk.X)
            
            # Label with required indicator
            label_text = f"{var_name}" + (" *" if required else "")
            label = tk.Label(
                frame,
                text=label_text,
                font=("Arial", 10, "bold"),
                width=25,
                anchor="w"
            )
            label.pack(side=tk.LEFT)
            
            # Entry field
            entry = tk.Entry(frame, width=30, font=("Arial", 10))
            entry.insert(0, default)
            entry.pack(side=tk.LEFT, padx=10)
            self.env_entries[var_name] = entry
            
            # Description
            desc = tk.Label(
                scrollable_frame,
                text=f"    {description}",
                font=("Arial", 9),
                fg="#666",
                anchor="w"
            )
            desc.pack(fill=tk.X, padx=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Result variable
        result = {"confirmed": False}
        
        def save_config():
            """Save configuration to .env file"""
            env_content = "# KOSMOS Environment Configuration\n"
            env_content += f"# Generated: {threading.current_thread().name}\n\n"
            
            for var_name, entry in self.env_entries.items():
                value = entry.get().strip()
                if value:
                    env_content += f"{var_name}={value}\n"
            
            # Save to .env file
            try:
                with open(".env", "w") as f:
                    f.write(env_content)
                result["confirmed"] = True
                messagebox.showinfo(
                    "Success",
                    "✅ Environment variables saved to .env file!"
                )
                dialog.destroy()
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to save .env file:\n{str(e)}"
                )
        
        def load_existing():
            """Load existing .env file if it exists"""
            if Path(".env").exists():
                try:
                    with open(".env", "r") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                key, value = line.split("=", 1)
                                if key in self.env_entries:
                                    self.env_entries[key].delete(0, tk.END)
                                    self.env_entries[key].insert(0, value)
                    messagebox.showinfo(
                        "Loaded",
                        "✅ Loaded existing .env configuration"
                    )
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Failed to load .env file:\n{str(e)}"
                    )
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        load_btn = tk.Button(
            button_frame,
            text="📂 Load Existing",
            font=("Arial", 10),
            command=load_existing,
            bg="#17a2b8",
            fg="white",
            padx=15,
            pady=5
        )
        load_btn.pack(side=tk.LEFT, padx=10)
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Save & Continue",
            font=("Arial", 10, "bold"),
            command=save_config,
            bg="#28a745",
            fg="white",
            padx=15,
            pady=5
        )
        save_btn.pack(side=tk.RIGHT, padx=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel",
            font=("Arial", 10),
            command=dialog.destroy,
            bg="#dc3545",
            fg="white",
            padx=15,
            pady=5
        )
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
        return result["confirmed"]
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
KOSMOS Setup Help

This application helps you set up your KOSMOS development environment.

Steps:
1. Select an environment option
2. Review the requirements and details
3. Click 'Start Setup'
4. Configure environment variables (.env)
5. Wait for completion (10-30 minutes)

For more information, see:
• DEVELOPMENT_ENVIRONMENT_GUIDE.md
• DEV_STAGE_AUTOMATION_ASSESSMENT.md

Need help? Create a GitHub issue.
        """
        messagebox.showinfo("Help", help_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = KosmosSetupGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
