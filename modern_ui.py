"""
Modern UI Components for AriTyper - Professional and Responsive Design
"""
import tkinter as tk
from tkinter import ttk, font, messagebox
import threading
import time
from typing import Optional, Callable, Dict, Any
import json

class ModernFrame(tk.Frame):
    """Modern frame with gradient background and rounded corners effect"""
    
    def __init__(self, parent, bg_color='#1a1a2e', accent_color='#00d4ff', **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        self.bg_color = bg_color
        self.accent_color = accent_color
        
    def add_header(self, title: str, subtitle: str = None):
        """Add a modern header to the frame"""
        header_frame = tk.Frame(self, bg=self.bg_color, height=80)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text=title,
            font=("Segoe UI", 24, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(anchor='w', pady=(20, 5))
        
        # Subtitle
        if subtitle:
            subtitle_label = tk.Label(
                header_frame,
                text=subtitle,
                font=("Segoe UI", 12),
                bg=self.bg_color,
                fg='#888888'
            )
            subtitle_label.pack(anchor='w')
        
        return header_frame

class ModernButton(tk.Button):
    """Modern button with hover effects and professional styling"""
    
    def __init__(self, parent, text: str, style: str = 'primary', **kwargs):
        self.style = style
        self.default_bg = self._get_style_color(style)
        self.hover_bg = self._get_hover_color(style)
        
        super().__init__(
            parent,
            text=text,
            bg=self.default_bg,
            fg='white',
            font=("Segoe UI", 11, "bold"),
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            **kwargs
        )
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _get_style_color(self, style: str) -> str:
        colors = {
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff6b6b',
            'secondary': '#6c757d'
        }
        return colors.get(style, '#00d4ff')
    
    def _get_hover_color(self, style: str) -> str:
        colors = {
            'primary': '#00a8cc',
            'success': '#00cc6a',
            'warning': '#ff8800',
            'danger': '#ff5252',
            'secondary': '#5a6268'
        }
        return colors.get(style, '#00a8cc')
    
    def _on_enter(self, event):
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.config(bg=self.default_bg)

class ModernCard(tk.Frame):
    """Modern card component with shadow effect"""
    
    def __init__(self, parent, title: str = None, **kwargs):
        super().__init__(parent, bg='#16213e', relief='flat', bd=0, **kwargs)
        
        self.content_frame = tk.Frame(self, bg='#16213e')
        self.content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        if title:
            title_label = tk.Label(
                self.content_frame,
                text=title,
                font=("Segoe UI", 14, "bold"),
                bg='#16213e',
                fg='white'
            )
            title_label.pack(anchor='w', pady=(0, 10))

class ModernProgressBar(tk.Canvas):
    """Modern progress bar with smooth animation"""
    
    def __init__(self, parent, width=300, height=20, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg='#1a1a2e',
            highlightthickness=0,
            **kwargs
        )
        self.width = width
        self.height = height
        self.progress = 0
        self.target_progress = 0
        
    def set_progress(self, value: float):
        """Set progress value (0-100)"""
        self.target_progress = max(0, min(100, value))
        self._animate_progress()
    
    def _animate_progress(self):
        """Animate progress change"""
        if abs(self.progress - self.target_progress) > 1:
            self.progress += (self.target_progress - self.progress) * 0.1
            self._draw_progress()
            self.after(20, self._animate_progress)
        else:
            self.progress = self.target_progress
            self._draw_progress()
    
    def _draw_progress(self):
        """Draw the progress bar"""
        self.delete("all")
        
        # Background
        self.create_rectangle(
            2, 2, self.width-2, self.height-2,
            fill='#0f3460',
            outline='#1e5f8e',
            width=1
        )
        
        # Progress
        progress_width = (self.width - 4) * (self.progress / 100)
        self.create_rectangle(
            2, 2, 2 + progress_width, self.height-2,
            fill='#00d4ff',
            outline='',
            width=0
        )
        
        # Text
        text = f"{self.progress:.0f}%"
        self.create_text(
            self.width/2, self.height/2,
            text=text,
            fill='white',
            font=("Segoe UI", 10, "bold")
        )

class ModernStatusIndicator(tk.Frame):
    """Modern status indicator with color coding"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg='#1a1a2e', **kwargs)
        
        self.canvas = tk.Canvas(
            self,
            width=12,
            height=12,
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.canvas.pack(side='left', padx=(0, 5))
        
        self.label = tk.Label(
            self,
            text="",
            font=("Segoe UI", 10),
            bg='#1a1a2e',
            fg='white'
        )
        self.label.pack(side='left')
        
        self.set_status('offline')
    
    def set_status(self, status: str, text: str = None):
        """Set status with color coding"""
        colors = {
            'online': '#00ff88',
            'offline': '#ff6b6b',
            'connecting': '#ffaa00',
            'active': '#00d4ff'
        }
        
        color = colors.get(status, '#888888')
        
        self.canvas.delete("all")
        self.canvas.create_oval(
            2, 2, 10, 10,
            fill=color,
            outline=''
        )
        
        if text:
            self.label.config(text=text)
        else:
            self.label.config(text=status.capitalize())

class ModernFileSelector(tk.Frame):
    """Modern file selector with drag-and-drop support"""
    
    def __init__(self, parent, file_types: list = None, on_file_selected: Callable = None, **kwargs):
        super().__init__(parent, bg='#1a1a2e', **kwargs)
        
        self.file_types = file_types or [("PDF files", "*.pdf"), ("Word files", "*.docx")]
        self.on_file_selected = on_file_selected
        self.selected_file = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the UI components"""
        # Drop area
        self.drop_frame = tk.Frame(
            self,
            bg='#16213e',
            relief='dashed',
            bd=2
        )
        self.drop_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Icon and text
        icon_label = tk.Label(
            self.drop_frame,
            text="📄",
            font=("Segoe UI", 24),
            bg='#16213e',
            fg='#00d4ff'
        )
        icon_label.pack(pady=(20, 10))
        
        self.info_label = tk.Label(
            self.drop_frame,
            text="Drop file here or click to browse",
            font=("Segoe UI", 11),
            bg='#16213e',
            fg='#888888'
        )
        self.info_label.pack(pady=(0, 20))
        
        # Browse button
        self.browse_btn = ModernButton(
            self.drop_frame,
            text="Browse Files",
            style='primary',
            command=self._browse_file
        )
        self.browse_btn.pack(pady=(0, 20))
        
        # Bind click event
        self.drop_frame.bind('<Button-1>', lambda e: self._browse_file())
    
    def _browse_file(self):
        """Browse for file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=self.file_types
        )
        
        if file_path:
            self._set_file(file_path)
    
    def _set_file(self, file_path: str):
        """Set the selected file"""
        self.selected_file = file_path
        filename = file_path.split('/')[-1].split('\\')[-1]
        
        self.info_label.config(
            text=f"Selected: {filename}",
            fg='#00ff88'
        )
        
        if self.on_file_selected:
            self.on_file_selected(file_path)
    
    def get_file(self) -> Optional[str]:
        """Get the selected file path"""
        return self.selected_file

class ModernTypingControls(tk.Frame):
    """Modern typing controls with real-time feedback"""
    
    def __init__(self, parent, on_start_typing: Callable = None, on_stop_typing: Callable = None, **kwargs):
        super().__init__(parent, bg='#1a1a2e', **kwargs)
        
        self.on_start_typing = on_start_typing
        self.on_stop_typing = on_stop_typing
        self.is_typing = False
        
        self._create_ui()
    
    def _create_ui(self):
        """Create typing controls UI"""
        # Speed control
        speed_frame = tk.Frame(self, bg='#1a1a2e')
        speed_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            speed_frame,
            text="Typing Speed:",
            font=("Segoe UI", 11),
            bg='#1a1a2e',
            fg='white'
        ).pack(side='left')
        
        self.speed_var = tk.DoubleVar(value=50)
        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=1,
            to=100,
            variable=self.speed_var,
            orient='horizontal',
            length=200
        )
        self.speed_scale.pack(side='left', padx=10)
        
        self.speed_label = tk.Label(
            speed_frame,
            text="50%",
            font=("Segoe UI", 10),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        self.speed_label.pack(side='left')
        
        # Update speed label
        self.speed_var.trace('w', self._update_speed_label)
        
        # Control buttons
        button_frame = tk.Frame(self, bg='#1a1a2e')
        button_frame.pack(fill='x')
        
        self.start_btn = ModernButton(
            button_frame,
            text="▶ Start Typing",
            style='success',
            command=self._start_typing
        )
        self.start_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = ModernButton(
            button_frame,
            text="⏹ Stop",
            style='danger',
            command=self._stop_typing,
            state='disabled'
        )
        self.stop_btn.pack(side='left')
        
        # Status indicator
        self.status_indicator = ModernStatusIndicator(self)
        self.status_indicator.pack(side='right')
    
    def _update_speed_label(self, *args):
        """Update speed label"""
        speed = int(self.speed_var.get())
        self.speed_label.config(text=f"{speed}%")
    
    def _start_typing(self):
        """Start typing"""
        self.is_typing = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_indicator.set_status('active', 'Typing...')
        
        if self.on_start_typing:
            self.on_start_typing()
    
    def _stop_typing(self):
        """Stop typing"""
        self.is_typing = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_indicator.set_status('offline', 'Stopped')
        
        if self.on_stop_typing:
            self.on_stop_typing()
    
    def get_speed(self) -> float:
        """Get typing speed (0-100)"""
        return self.speed_var.get()

class ModernWindowManager:
    """Modern window management with responsive design"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
    def setup_window(self):
        """Setup modern window properties"""
        self.root.title("AriTyper - Professional Document Typing")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0f0f23')
        self.root.minsize(800, 600)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
        # Modern styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Modern.TFrame', background='#1a1a2e')
        style.configure('Modern.TLabel', background='#1a1a2e', foreground='white')
        
        # Handle window resize
        self.root.bind('<Configure>', self._on_resize)
    
    def _on_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            # Responsive adjustments
            width = event.width
            height = event.height
            
            # Adjust font sizes based on window size
            if width < 1000:
                font_size = 10
            elif width < 1400:
                font_size = 11
            else:
                font_size = 12
            
            # Update UI elements if needed
            self.root.update_idletasks()

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    window_manager = ModernWindowManager(root)
    
    # Create main modern frame
    main_frame = ModernFrame(root)
    main_frame.pack(fill='both', expand=True)
    
    # Add header
    header = main_frame.add_header(
        "AriTyper Modern UI",
        "Professional Document Typing Software"
    )
    
    # Add components
    card = ModernCard(main_frame, "File Selection")
    card.pack(fill='x', padx=20, pady=10)
    
    file_selector = ModernFileSelector(card.content_frame)
    file_selector.pack(fill='x', pady=10)
    
    typing_controls = ModernTypingControls(main_frame)
    typing_controls.pack(fill='x', padx=20, pady=10)
    
    root.mainloop()
