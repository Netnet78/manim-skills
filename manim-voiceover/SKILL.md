---
name: manim-voiceover
description: >-
  Audio, subcaptions (.srt), synchronized TTS/microphone narration with
  manim-voiceover, word-level bookmarks, and Manim plugins. Use when adding
  sound effects, narration, subtitles, or third-party Manim plugins to a scene.
version: 0.22.0
---

# Manim Audio, Subcaptions, Voiceovers & Plugins

For general Manim rules and rendering workflow, see [manim-best-practices](../manim-best-practices/SKILL.md).

---

## 1. Critical Rule: Disable Caching When Using Audio

Manim's partial-movie caching skips `Scene.add_sound()` calls on cached segments, which causes missing audio in final renders (both native `self.add_sound()` and `manim-voiceover`).

Always pass `--disable_caching` on the CLI or set it in `manim.cfg` / Python whenever a scene uses audio:

```bash
manim -ql --disable_caching scene.py NarratedScene
```

```ini
# manim.cfg
[CLI]
disable_caching = True
```

---

## 2. Native Sound Effects (`Scene.add_sound`)

Add WAV/MP3/OGG sound effects at the current `self.time` timestamp without external plugins:

```python
from manim import *

class SoundEffectsDemo(Scene):
    def construct(self):
        dot = Dot(color=GREEN)
        self.add_sound("assets/click.wav")                  # plays at t = 0.0s
        self.play(FadeIn(dot, scale=0.5), run_time=0.5)

        self.add_sound("assets/whoosh.wav", time_offset=0.1, gain=-6)
        self.play(dot.animate.shift(RIGHT * 3), run_time=1.0)
        self.wait(0.5)
```

- `sound_file`: Path to audio file (relative to working directory or in `assets/`).
- `time_offset` (`float`, seconds): Offset relative to the current `self.time` when playback starts (can be positive or negative).
- `gain` (`float | None`, dB): Volume adjustment in decibels (negative attenuates, positive amplifies).

---

## 3. Native `.srt` Subcaptions

Manim natively writes an `.srt` subtitle file alongside the rendered video file (`media/videos/<module>/<quality>/<SceneName>.srt`) when subcaptions are registered:

```python
class SubcaptionDemo(Scene):
    def construct(self):
        sq = Square(color=BLUE)
        circ = Circle(color=RED)

        # Option A: Tied directly to a self.play() call (duration defaults to run_time)
        self.play(
            Create(sq),
            subcaption="First, construct a blue square.",
            subcaption_duration=None,  # defaults to animation run_time
            subcaption_offset=0.0,
        )

        # Option B: Standalone timestamped entry at current self.time
        self.add_subcaption("Watch carefully...", duration=1.0, offset=0.0)
        self.wait(1.0)

        self.play(
            ReplacementTransform(sq, circ),
            subcaption="Now morph the square into a circle.",
        )
```

---

## 4. Synchronized Narration with `manim-voiceover`

[`manim-voiceover`](https://voiceover.manim.community/) lets you write voiceover scripts directly inside `construct()`, automatically driving animation durations from TTS or recorded microphone audio and generating `.srt` subcaptions automatically.

### Installation

```bash
# uv (recommended)
uv add "manim-voiceover[gtts,azure]"

# Or pip — pick the extras matching your speech service(s):
pip install "manim-voiceover[gtts]"                 # Free Google Translate TTS (needs internet)
pip install "manim-voiceover[openai]"               # OpenAI TTS (OPENAI_API_KEY in .env)
pip install "manim-voiceover[azure]"                # Azure Neural TTS (native bookmark support!)
pip install "manim-voiceover[elevenlabs]"           # ElevenLabs TTS (ELEVEN_API_KEY in .env)
pip install "manim-voiceover[recorder]"             # CLI microphone recording (requires PortAudio/PyAudio)
pip install "manim-voiceover[transcribe]"           # Whisper word-level bookmarks for non-Azure services
```

System prerequisites for optional features:
- **Microphone recording (`recorder`)**: Requires `PyAudio` (`PortAudio` comes bundled on Windows wheels; `brew install portaudio` on macOS; `sudo apt install portaudio19-dev` on Debian/Ubuntu).
- **Audio speed adjustment**: Requires `SoX` >= 14.4.2 (`brew install sox` / `sudo apt install sox libsox-fmt-all`).

### Core `VoiceoverScene` Pattern

Inherit from `VoiceoverScene` (or combine via multiple inheritance, e.g. `class MyScene(MovingCameraScene, VoiceoverScene):` or `class My3DScene(ThreeDScene, VoiceoverScene):`):

```python
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class VoiceoverDemo(VoiceoverScene):
    def construct(self):
        # Swap GTTSService() -> RecorderService() or AzureService(...) for final production!
        self.set_speech_service(GTTSService(lang="en", tld="com"))

        circle = Circle(color=BLUE, fill_opacity=0.3)

        # If animations inside the block finish early, Manim automatically waits
        # until the spoken sentence completes before exiting the `with` block.
        with self.voiceover(text="This circle is drawn at the exact pace I speak.") as tracker:
            self.play(Create(circle), run_time=tracker.duration)

        # Override on-screen .srt text when spoken phonetics differ from display math:
        with self.voiceover(
            text="Now we shift it left by pi over two units.",
            subcaption="Now we shift it left by π/2 units.",
        ) as tracker:
            self.play(circle.animate.shift(LEFT * (PI / 2)), run_time=tracker.duration)
```

To disable automatic `.srt` generation globally, pass `create_subcaption=False` to `self.set_speech_service(..., create_subcaption=False)`.

### Speech Services Quick Reference

| Service | Import (`manim_voiceover.services.*`) | `.env` Credentials | Notes |
| :--- | :--- | :--- | :--- |
| **gTTS** | `from ...gtts import GTTSService` | None | Free, zero-auth; best for fast prototyping |
| **Recorder** | `from ...recorder import RecorderService` | None | Interactive CLI mic recording during render |
| **Azure** | `from ...azure import AzureService` | `AZURE_SUBSCRIPTION_KEY`, `AZURE_SERVICE_REGION` | Native SSML word-boundary `<bookmark/>` support (no Whisper needed) |
| **OpenAI** | `from ...openai import OpenAIService` | `OPENAI_API_KEY` | `OpenAIService(voice="alloy", model="tts-1-hd")` |
| **ElevenLabs** | `from ...elevenlabs import ElevenLabsService` | `ELEVEN_API_KEY` | Natural & cloned voices |
| **Coqui** | `from ...coqui import CoquiService` | None | Local neural TTS (PyTorch) |
| **pyttsx3** | `from ...pyttsx3 import PyTTSX3Service` | None | Offline system `espeak` / SAPI5 synth |

**Recommended Production Workflow**: Draft and iterate animations with `GTTSService()`, then change **one line** (`self.set_speech_service(RecorderService())` or `AzureService(voice="en-US-AriaNeural", style="newscast-casual")`) for final rendering—all `tracker.duration` and bookmark timings automatically adapt.

### Word- & Syllable-Level Sync with Bookmarks

Insert `<bookmark mark='ID'/>` tags inside `text` to trigger animations at exact words or syllables:

```python
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
# For non-Azure services (gTTS, OpenAI, Recorder, ElevenLabs), pass transcription_model="base"
# (requires `pip install "manim-voiceover[transcribe]"`):
# self.set_speech_service(GTTSService(transcription_model="base"))

class BookmarkSyncDemo(VoiceoverScene):
    def construct(self):
        self.set_speech_service(AzureService(voice="en-US-AriaNeural"))

        eq = MathTex("E", "=", "m", "c^2", font_size=72)

        with self.voiceover(
            text="Einstein showed that <bookmark mark='E'/>energy equals "
                 "<bookmark mark='m'/>mass times the <bookmark mark='c'/>speed of light squared."
        ) as tracker:
            self.wait_until_bookmark("E")
            self.play(
                Write(eq[0:2]),
                run_time=tracker.time_until_bookmark("m", limit=1.0),
            )

            self.wait_until_bookmark("m")
            self.play(
                Write(eq[2]),
                run_time=tracker.time_until_bookmark("c", limit=1.0),
            )

            self.wait_until_bookmark("c")
            self.play(Write(eq[3]), run_time=tracker.get_remaining_duration())

        with self.voiceover(text="Let's pause one second before the end to fade out.") as tracker:
            # safe_wait avoids ValueError if remaining duration <= 1.0s
            self.safe_wait(tracker.get_remaining_duration() - 1.0)
            self.play(FadeOut(eq), run_time=1.0)
```

Key `TimeTracker` & `VoiceoverScene` helpers:
- `tracker.duration`: Total duration (seconds) of the current voiceover clip.
- `tracker.get_remaining_duration(buff=0.0)`: Seconds left from `self.time` until the end of the voiceover.
- `self.wait_until_bookmark("A")`: Waits from the current scene timestamp until bookmark `'A'` is spoken.
- `tracker.time_until_bookmark("B", buff=0.0, limit=None)`: Duration in seconds from the current scene timestamp until bookmark `'B'`, optionally capped at `limit` seconds.
- `self.safe_wait(duration)`: Calls `self.wait(duration)` only when `duration > 1 / config.frame_rate` (prevents negative/zero wait errors when subtracting animation lengths).

---

## 5. Manim Plugin Ecosystem

Official directory: <https://plugins.manim.community/>

### Popular Community Plugins
- **`manim-voiceover`**: Synchronized TTS / microphone voiceovers and bookmarks.
- **`manim-slides`**: Interactive slide-deck presentations (PowerPoint/Reveal.js style) built from Manim scenes.
- **`manim-physics`**: Rigid-body mechanics (Pymunk), electromagnetism, pendulums, waves, and optics.
- **`manim-chemistry`**: 2D/3D molecular structures, orbitals, periodic tables, and Bohr atoms.
- **`manim-ml`**: Neural network architectures, convolutional layers, and machine learning visualizations.
- **`manim-dsa`**: Data structures and algorithms (arrays, trees, graphs, stacks, sorting visualizations).

### Managing & Using Plugins

1. **Install & list discovered plugins**:
   ```bash
   uv add manim-physics
   manim plugins -l
   ```
2. **Import explicitly in Python (Required since Manim v0.18.1+)**:
   ```python
   from manim import *
   from manim_physics import *
   ```
   *(If enabling via `manim.cfg` `[CLI] plugins = manim_physics`, always use the **Python module name with underscores**, never the PyPI hyphenated package name.)*

### Authoring a Custom Plugin
1. Expose a `"manim.plugins"` entry point in `pyproject.toml`:
   ```toml
   [project.entry-points."manim.plugins"]
   "manim_myplugin" = "manim_myplugin"
   ```
2. **Cairo + OpenGL Renderer Compatibility**: Custom mobjects subclassing `Mobject` or `VMobject` can support both `--renderer=cairo` and `--renderer=opengl` automatically via the `ConvertToOpenGL` metaclass:
   ```python
   from manim import VMobject
   from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL

   class CustomBadge(VMobject, metaclass=ConvertToOpenGL):
       ...
   ```
