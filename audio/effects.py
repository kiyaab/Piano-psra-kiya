"""
KIYA Piano Studio Pro - Real-time DSP Effects Processor
Includes 3-Band EQ, Stereo Reverb, Stereo Chorus, Stereo Delay, and Master Limiter.
All processors operate on float32 NumPy audio buffers [frames, 2].
"""

import math
import numpy as np

class DSPBiquad:
    """Bi-quad IIR filter for parametric EQ."""
    def __init__(self, filter_type: str, freq: float, sample_rate: float, gain_db: float = 0.0, q: float = 0.707):
        self.sample_rate = sample_rate
        self.filter_type = filter_type
        self.freq = freq
        self.gain_db = gain_db
        self.q = q
        self.x1 = np.zeros(2, dtype=np.float32)
        self.x2 = np.zeros(2, dtype=np.float32)
        self.y1 = np.zeros(2, dtype=np.float32)
        self.y2 = np.zeros(2, dtype=np.float32)
        self._calc_coeffs()

    def set_params(self, freq: float = None, gain_db: float = None, q: float = None):
        if freq is not None:
            self.freq = max(20.0, min(self.sample_rate * 0.45, freq))
        if gain_db is not None:
            self.gain_db = max(-24.0, min(24.0, gain_db))
        if q is not None:
            self.q = max(0.1, min(10.0, q))
        self._calc_coeffs()

    def _calc_coeffs(self):
        w0 = 2.0 * math.pi * self.freq / self.sample_rate
        cos_w0 = math.cos(w0)
        sin_w0 = math.sin(w0)
        alpha = sin_w0 / (2.0 * self.q)
        A = 10.0 ** (self.gain_db / 40.0)

        if self.filter_type == "low_shelf":
            two_sqrt_a_alpha = 2.0 * math.sqrt(A) * alpha
            a0 = (A + 1.0) + (A - 1.0) * cos_w0 + two_sqrt_a_alpha
            self.b0 = A * ((A + 1.0) - (A - 1.0) * cos_w0 + two_sqrt_a_alpha) / a0
            self.b1 = 2.0 * A * ((A - 1.0) - (A + 1.0) * cos_w0) / a0
            self.b2 = A * ((A + 1.0) - (A - 1.0) * cos_w0 - two_sqrt_a_alpha) / a0
            self.a1 = -2.0 * ((A - 1.0) + (A + 1.0) * cos_w0) / a0
            self.a2 = ((A + 1.0) + (A - 1.0) * cos_w0 - two_sqrt_a_alpha) / a0
        elif self.filter_type == "high_shelf":
            two_sqrt_a_alpha = 2.0 * math.sqrt(A) * alpha
            a0 = (A + 1.0) - (A - 1.0) * cos_w0 + two_sqrt_a_alpha
            self.b0 = A * ((A + 1.0) + (A - 1.0) * cos_w0 + two_sqrt_a_alpha) / a0
            self.b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w0) / a0
            self.b2 = A * ((A + 1.0) + (A - 1.0) * cos_w0 - two_sqrt_a_alpha) / a0
            self.a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w0) / a0
            self.a2 = ((A + 1.0) - (A - 1.0) * cos_w0 - two_sqrt_a_alpha) / a0
        else:  # peaking eq
            a0 = 1.0 + alpha / A
            self.b0 = (1.0 + alpha * A) / a0
            self.b1 = (-2.0 * cos_w0) / a0
            self.b2 = (1.0 - alpha * A) / a0
            self.a1 = (-2.0 * cos_w0) / a0
            self.a2 = (1.0 - alpha / A) / a0

    def process(self, buffer: np.ndarray) -> np.ndarray:
        if abs(self.gain_db) < 0.05:
            return buffer
        out = np.empty_like(buffer)
        b0, b1, b2 = self.b0, self.b1, self.b2
        a1, a2 = self.a1, self.a2

        # Fast direct form I processing per channel
        for ch in (0, 1):
            x = buffer[:, ch]
            y = np.empty_like(x)
            x1, x2 = self.x1[ch], self.x2[ch]
            y1, y2 = self.y1[ch], self.y2[ch]
            for n in range(len(x)):
                xn = x[n]
                yn = b0 * xn + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
                y[n] = yn
                x2, x1 = x1, xn
                y2, y1 = y1, yn
            self.x1[ch], self.x2[ch] = x1, x2
            self.y1[ch], self.y2[ch] = y1, y2
            out[:, ch] = y
        return out


class StereoDelay:
    """Stereo delay with feedback and damping."""
    def __init__(self, sample_rate: int = 44100, max_delay_sec: float = 1.5):
        self.sample_rate = sample_rate
        self.max_frames = int(max_delay_sec * sample_rate)
        self.buffer = np.zeros((self.max_frames, 2), dtype=np.float32)
        self.write_pos = 0
        self.delay_time = 0.35  # seconds
        self.feedback = 0.40
        self.mix = 0.0  # 0.0 = bypass

    def set_params(self, delay_time: float = None, feedback: float = None, mix: float = None):
        if delay_time is not None:
            self.delay_time = max(0.01, min(1.2, delay_time))
        if feedback is not None:
            self.feedback = max(0.0, min(0.85, feedback))
        if mix is not None:
            self.mix = max(0.0, min(1.0, mix))

    def process(self, input_buf: np.ndarray) -> np.ndarray:
        if self.mix <= 0.001:
            return input_buf
        n_frames = len(input_buf)
        delay_frames_l = int(self.delay_time * self.sample_rate)
        delay_frames_r = int((self.delay_time * 1.05) * self.sample_rate)  # stereo ping-pong offset

        out = np.copy(input_buf)
        for i in range(n_frames):
            read_pos_l = (self.write_pos - delay_frames_l + self.max_frames) % self.max_frames
            read_pos_r = (self.write_pos - delay_frames_r + self.max_frames) % self.max_frames

            del_l = self.buffer[read_pos_l, 0]
            del_r = self.buffer[read_pos_r, 1]

            out[i, 0] += del_l * self.mix
            out[i, 1] += del_r * self.mix

            # Write feedback to buffer
            self.buffer[self.write_pos, 0] = input_buf[i, 0] + del_r * self.feedback
            self.buffer[self.write_pos, 1] = input_buf[i, 1] + del_l * self.feedback

            self.write_pos = (self.write_pos + 1) % self.max_frames
        return out


class StereoChorus:
    """Stereo chorus effect with dual modulated LFOs."""
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.max_delay = int(0.05 * sample_rate)
        self.buffer = np.zeros((self.max_delay, 2), dtype=np.float32)
        self.write_pos = 0
        self.rate = 1.2  # Hz
        self.depth = 0.0035  # seconds
        self.mix = 0.0
        self.lfo_phase = 0.0

    def set_params(self, rate: float = None, depth: float = None, mix: float = None):
        if rate is not None:
            self.rate = max(0.1, min(8.0, rate))
        if depth is not None:
            self.depth = max(0.001, min(0.015, depth))
        if mix is not None:
            self.mix = max(0.0, min(1.0, mix))

    def process(self, input_buf: np.ndarray) -> np.ndarray:
        if self.mix <= 0.001:
            return input_buf
        n_frames = len(input_buf)
        base_delay_samples = 0.015 * self.sample_rate
        depth_samples = self.depth * self.sample_rate
        lfo_step = (2.0 * math.pi * self.rate) / self.sample_rate

        out = np.copy(input_buf)
        for i in range(n_frames):
            # Left LFO and Right LFO (90 deg out of phase)
            mod_l = math.sin(self.lfo_phase) * depth_samples
            mod_r = math.cos(self.lfo_phase) * depth_samples
            self.lfo_phase = (self.lfo_phase + lfo_step) % (2.0 * math.pi)

            # Circular read positions with linear interpolation
            d_l = base_delay_samples + mod_l
            d_r = base_delay_samples + mod_r

            read_idx_l = self.write_pos - d_l
            if read_idx_l < 0:
                read_idx_l += self.max_delay
            idx_int_l = int(read_idx_l)
            frac_l = read_idx_l - idx_int_l
            samp_l = (1.0 - frac_l) * self.buffer[idx_int_l, 0] + frac_l * self.buffer[(idx_int_l + 1) % self.max_delay, 0]

            read_idx_r = self.write_pos - d_r
            if read_idx_r < 0:
                read_idx_r += self.max_delay
            idx_int_r = int(read_idx_r)
            frac_r = read_idx_r - idx_int_r
            samp_r = (1.0 - frac_r) * self.buffer[idx_int_r, 1] + frac_r * self.buffer[(idx_int_r + 1) % self.max_delay, 1]

            out[i, 0] += samp_l * self.mix
            out[i, 1] += samp_r * self.mix

            self.buffer[self.write_pos, 0] = input_buf[i, 0]
            self.buffer[self.write_pos, 1] = input_buf[i, 1]
            self.write_pos = (self.write_pos + 1) % self.max_delay
        return out


class SchroederReverb:
    """Freeverb-style stereo Schroeder reverberator."""
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.mix = 0.30
        self.room_size = 0.75
        self.damp = 0.25

        # 4 Comb filter delay lengths (in samples) per channel
        scale = sample_rate / 44100.0
        comb_tunings_l = [int(x * scale) for x in [1116, 1188, 1277, 1356]]
        comb_tunings_r = [int(x * scale) for x in [1139, 1211, 1300, 1379]]

        self.comb_buffers_l = [np.zeros(size, dtype=np.float32) for size in comb_tunings_l]
        self.comb_buffers_r = [np.zeros(size, dtype=np.float32) for size in comb_tunings_r]
        self.comb_pos_l = [0] * 4
        self.comb_pos_r = [0] * 4
        self.comb_filter_l = [0.0] * 4
        self.comb_filter_r = [0.0] * 4

        # 2 Allpass filters per channel
        allpass_tunings = [int(x * scale) for x in [556, 441]]
        self.allpass_buffers_l = [np.zeros(size, dtype=np.float32) for size in allpass_tunings]
        self.allpass_buffers_r = [np.zeros(size, dtype=np.float32) for size in allpass_tunings]
        self.allpass_pos_l = [0] * 2
        self.allpass_pos_r = [0] * 2

    def set_params(self, room_size: float = None, damp: float = None, mix: float = None):
        if room_size is not None:
            self.room_size = max(0.1, min(0.98, room_size))
        if damp is not None:
            self.damp = max(0.0, min(0.9, damp))
        if mix is not None:
            self.mix = max(0.0, min(1.0, mix))

    def process(self, input_buf: np.ndarray) -> np.ndarray:
        if self.mix <= 0.001:
            return input_buf
        n_frames = len(input_buf)
        out = np.copy(input_buf)
        feedback = self.room_size
        damp1 = 1.0 - self.damp
        damp2 = self.damp

        rev_l = np.zeros(n_frames, dtype=np.float32)
        rev_r = np.zeros(n_frames, dtype=np.float32)

        # Sum combs
        for n in range(n_frames):
            in_mono = (input_buf[n, 0] + input_buf[n, 1]) * 0.5

            # Process 4 combs Left
            sum_l = 0.0
            for c in range(4):
                buf = self.comb_buffers_l[c]
                pos = self.comb_pos_l[c]
                out_samp = buf[pos]
                self.comb_filter_l[c] = out_samp * damp1 + self.comb_filter_l[c] * damp2
                buf[pos] = in_mono + self.comb_filter_l[c] * feedback
                self.comb_pos_l[c] = (pos + 1) % len(buf)
                sum_l += out_samp

            # Process 4 combs Right
            sum_r = 0.0
            for c in range(4):
                buf = self.comb_buffers_r[c]
                pos = self.comb_pos_r[c]
                out_samp = buf[pos]
                self.comb_filter_r[c] = out_samp * damp1 + self.comb_filter_r[c] * damp2
                buf[pos] = in_mono + self.comb_filter_r[c] * feedback
                self.comb_pos_r[c] = (pos + 1) % len(buf)
                sum_r += out_samp

            rev_l[n] = sum_l * 0.25
            rev_r[n] = sum_r * 0.25

        # Process Allpasses
        for a in range(2):
            buf_l = self.allpass_buffers_l[a]
            buf_r = self.allpass_buffers_r[a]
            pos_l = self.allpass_pos_l[a]
            pos_r = self.allpass_pos_r[a]
            len_l = len(buf_l)
            len_r = len(buf_r)
            for n in range(n_frames):
                # Left
                buf_val = buf_l[pos_l]
                y_l = -rev_l[n] + buf_val
                buf_l[pos_l] = rev_l[n] + buf_val * 0.5
                pos_l = (pos_l + 1) % len_l
                rev_l[n] = y_l

                # Right
                buf_val_r = buf_r[pos_r]
                y_r = -rev_r[n] + buf_val_r
                buf_r[pos_r] = rev_r[n] + buf_val_r * 0.5
                pos_r = (pos_r + 1) % len_r
                rev_r[n] = y_r
            self.allpass_pos_l[a] = pos_l
            self.allpass_pos_r[a] = pos_r

        out[:, 0] += rev_l * self.mix
        out[:, 1] += rev_r * self.mix
        return out


class MasterLimiter:
    """Soft-knee limiter to prevent clipping and ear fatigue."""
    @staticmethod
    def process(buffer: np.ndarray, ceiling: float = 0.95) -> np.ndarray:
        # np.tanh provides clean analog-style soft saturation above ceiling
        peak = np.max(np.abs(buffer))
        if peak > ceiling:
            scale = ceiling / peak
            # Apply smooth soft knee
            return np.tanh(buffer * scale) * ceiling
        return buffer


class EffectsChain:
    """Consolidated master effects chain."""
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.eq_low = DSPBiquad("low_shelf", 220.0, sample_rate, 0.0)
        self.eq_mid = DSPBiquad("peaking", 1200.0, sample_rate, 0.0, q=1.0)
        self.eq_high = DSPBiquad("high_shelf", 5500.0, sample_rate, 0.0)
        self.chorus = StereoChorus(sample_rate)
        self.delay = StereoDelay(sample_rate)
        self.reverb = SchroederReverb(sample_rate)
        self.limiter = MasterLimiter()

    def process(self, buffer: np.ndarray) -> np.ndarray:
        # EQ -> Chorus -> Delay -> Reverb -> Limiter
        out = self.eq_low.process(buffer)
        out = self.eq_mid.process(out)
        out = self.eq_high.process(out)
        out = self.chorus.process(out)
        out = self.delay.process(out)
        out = self.reverb.process(out)
        out = self.limiter.process(out)
        return out
