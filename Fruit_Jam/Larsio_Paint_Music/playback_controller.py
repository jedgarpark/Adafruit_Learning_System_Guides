# SPDX-FileCopyrightText: 2025 John Park and Claude AI for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
Playback controller for CircuitPython Music Staff Application.
Manages the playback state, button displays, and sound triggering.
"""

import time

# pylint: disable=trailing-whitespace, too-many-instance-attributes
class PlaybackController:
    """Manages playback state and controls"""

    def __init__(self, sound_manager, note_manager, seconds_per_eighth=0.25):
        """Initialize the playback controller with sound and note managers"""
        self.sound_manager = sound_manager
        self.note_manager = note_manager
        self.seconds_per_eighth = seconds_per_eighth

        # Playback state
        self.is_playing = False
        self.playhead_position = -1
        self.last_playhead_time = 0
        self.loop_enabled = False

        # UI elements (to be set externally)
        self.playhead = None
        self.play_button = None
        self.play_button_bitmap = None
        self.stop_button = None
        self.stop_button_bitmap = None

        # Button sprites (will be set in set_ui_elements)
        self.button_sprites = None

    def set_ui_elements(self, playhead, play_button, stop_button, button_sprites=None):
        """Set references to UI elements needed for playback control"""
        self.playhead = playhead
        self.play_button = play_button
        self.stop_button = stop_button
        self.button_sprites = button_sprites

    def start_playback(self, start_margin=25):
        """Start playback"""
        self.is_playing = True
        self.playhead_position = -1  # Start at -1 so first note plays immediately
        self.last_playhead_time = time.monotonic()

        # Set playhead position to just before the first note
        self.playhead.x = start_margin - 5

        # Update button states using bitmaps
        if hasattr(self, 'button_sprites') and self.button_sprites is not None:
            # Update play button to "down" state
            self.play_button.bitmap = self.button_sprites['play']['down'][0]
            self.play_button.pixel_shader = self.button_sprites['play']['down'][1]

            # Update stop button to "up" state
            self.stop_button.bitmap = self.button_sprites['stop']['up'][0]
            self.stop_button.pixel_shader = self.button_sprites['stop']['up'][1]
        else:
            # Fallback implementation for drawn buttons
            # Note: This section is for backward compatibility but has issues
            # Ideally, button_sprites should always be provided
            print("Warning: Using fallback button display (not fully supported)")
            # The fallback code is intentionally omitted as it has errors
            # and requires refactoring of the bitmap handling

        print("Playback started")

    def stop_playback(self):
        """Stop playback"""
        self.sound_manager.stop_all_notes()
        self.is_playing = False
        self.playhead.x = -10  # Move off-screen

        # Update button states using bitmaps
        if hasattr(self, 'button_sprites') and self.button_sprites is not None:
            # Update play button to "up" state
            self.play_button.bitmap = self.button_sprites['play']['up'][0]
            self.play_button.pixel_shader = self.button_sprites['play']['up'][1]

            # Update stop button to "down" state
            self.stop_button.bitmap = self.button_sprites['stop']['down'][0]
            self.stop_button.pixel_shader = self.button_sprites['stop']['down'][1]
        else:
            # Fallback implementation for drawn buttons
            # Note: This section is for backward compatibility but has issues
            # Ideally, button_sprites should always be provided
            print("Warning: Using fallback button display (not fully supported)")
            # The fallback code is intentionally omitted as it has errors
            # and requires refactoring of the bitmap handling

        print("Playback stopped")

    def set_tempo(self, seconds_per_eighth):
        """Update the playback tempo"""
        self.seconds_per_eighth = seconds_per_eighth
        print(f"Playback tempo updated: {60 / (seconds_per_eighth * 2)} BPM")

    def update_playback(self, x_positions):
        """Update playback state and play notes at current position"""
        if not self.is_playing:
            return

        current_time = time.monotonic()
        elapsed = current_time - self.last_playhead_time

        # Move at tempo rate
        if elapsed >= self.seconds_per_eighth:
            # Stop all current active notes
            self.sound_manager.stop_all_notes()

            # Move playhead to next eighth note position
            self.playhead_position += 1
            self.last_playhead_time = current_time

            # Check if we've reached the end
            if self.playhead_position >= len(x_positions):
                if self.loop_enabled:
                    # Loop back to the beginning
                    self.playhead_position = 0
                    self.playhead.x = x_positions[0] - 1
                else:
                    # Stop playback if not looping
                    self.stop_playback()
                    return

            # Update playhead position
            self.playhead.x = x_positions[self.playhead_position] - 1

            # Find all notes at current playhead position
            current_x = x_positions[self.playhead_position]
            notes_at_position = []

            for x_pos, y_pos, midi_note, channel in self.note_manager.note_data:
                if abs(x_pos - current_x) < 2:  # Note is at current position
                    notes_at_position.append((x_pos, y_pos, midi_note, channel))

            # Play all notes at the current position
            if notes_at_position:
                self.sound_manager.play_notes_at_position(notes_at_position)
