import time
import pygetwindow as gw
import os
from pynput.keyboard import Controller
import mido

# 按键映射 (光遇按键范围)
note_to_key_mapping = {
    60: 'y',  # C4
    62: 'u',  # D4
    64: 'i',  # E4
    65: 'o',  # F4
    67: 'p',  # G4
    69: 'h',  # A4
    71: 'j',  # B4
    72: 'k',  # C5
    74: 'l',  # D5
    76: ';',  # E5
    77: 'n',  # F5
    79: 'm',  # G5
    81: ',',  # A5
    83: '.',  # B5
    84: '/',  # C6
    # 可以根据需要继续添加更多音符
}

# 键盘控制器
keyboard = Controller()

# 解析 MIDI 文件
def parse_midi(file_path):
    try:
        midi = mido.MidiFile(file_path)
        notes = []
        current_time = 0.0

        for msg in midi:
            current_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                key = note_to_key_mapping.get(msg.note)
                if key:
                    notes.append({'key': key, 'time': current_time})
                    current_time = 0.0

        key_sequence = [note['key'] for note in notes]
        delays = [note['time'] for note in notes]
        return key_sequence, delays
    except Exception as e:
        print(f"解析 MIDI 文件时出错: {e}")
        return None, None

# 切换到游戏窗口
def switch_to_game():
    try:
        windows = gw.getWindowsWithTitle("光·遇")
        if not windows:
            print("未找到游戏窗口。请确认游戏已启动。")
            return False
        game_window = windows[0]
        game_window.activate()
        time.sleep(1)
        return True
    except Exception as e:
        print(f"切换窗口时出错: {e}")
        return False

# 模拟播放
def play_song(keys, delays):
    if not keys or not delays:
        print("按键序列或延迟为空！")
        return

    try:
        for key, delay in zip(keys, delays):
            print(f"按下 {key}, 等待 {delay:.2f} 秒")
            keyboard.press(key)
            time.sleep(0.02)  # 确保按键有足够时间按下
            keyboard.release(key)
            time.sleep(max(delay, 0.00))  # 确保延迟不为负
    except Exception as e:
        print(f"播放时出错: {e}")

# 主函数
def main():
    file_path = input("请输入 MIDI 文件路径：").strip()
    if not os.path.exists(file_path):
        print("文件不存在！")
        return

    print("正在解析 MIDI 文件...")
    keys, delays = parse_midi(file_path)
    if keys and delays:
        print(f"解析成功，共 {len(keys)} 个音符")
        if not switch_to_game():
            print("切换到游戏窗口失败，请手动切换。")
            return
        print("5 秒后开始播放...")
        time.sleep(5)
        play_song(keys, delays)
    else:
        print("解析失败，请检查 MIDI 文件。")

if __name__ == "__main__":
    main()