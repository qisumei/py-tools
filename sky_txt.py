import json
import os
import time
from pynput.keyboard import Controller

# 按键映射 (光遇按键范围)
note_to_key_mapping = {
    '1Key0': 'y',  # C4
    '1Key1': 'u',  # D4
    '1Key2': 'i',  # E4
    '1Key3': 'o',  # F4
    '1Key4': 'p',  # G4
    '1Key5': 'h',  # A4
    '1Key6': 'j',  # B4
    '1Key7': 'k',  # C5
    '1Key8': 'l',  # D5
    '1Key9': ';',  # E5
    '1Key10': 'n',  # F5
    '1Key11': 'm',  # G5
    '1Key12': ',',  # A5
    '1Key13': '.',  # B5
    '1Key14': '/',  # C6
    '2Key0': 'y',  # C4
    '2Key1': 'u',  # D4
    '2Key2': 'i',  # E4
    '2Key3': 'o',  # F4
    '2Key4': 'p',  # G4
    '2Key5': 'h',  # A4
    '2Key6': 'j',  # B4
    '2Key7': 'k',  # C5
    '2Key8': 'l',  # D5
    '2Key9': ';',  # E5
    '2Key10': 'n',  # F5
    '2Key11': 'm',  # G5
    '2Key12': ',',  # A5
    '2Key13': '.',  # B5
    '2Key14': '/',  # C6
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

# 解析乐谱文件
def parse_score(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            score_data = json.load(file)
            notes = score_data[0]['songNotes']
            notes.sort(key=lambda x: x['time'])

            key_sequence = []
            delays = []
            previous_time = 0

            for note in notes:
                key = note_to_key_mapping.get(note['key'])
                if key:
                    key_sequence.append(key)
                    delay = (note['time'] - previous_time) / 1000  # 转换为秒
                    delays.append(delay)
                    previous_time = note['time']

            return key_sequence, delays
    except Exception as e:
        print(f"解析乐谱文件时出错: {e}")
        return None, None

# 模拟播放
def play_song(keys, delays):
    if not keys or not delays:
        print("按键序列或延迟为空！")
        return

    try:
        for key, delay in zip(keys, delays):
            print(f"按下 {key}, 等待 {delay:.2f} 秒")
            keyboard.press(key)
            time.sleep(0.001)  # 确保按键有足够时间按下
            keyboard.release(key)
            time.sleep(max(delay, 0.00))  # 确保延迟不为负
    except Exception as e:
        print(f"播放时出错: {e}")

# 主函数
def main():
    file_path = input("请输入乐谱文件路径：").strip()
    if not os.path.exists(file_path):
        print("文件不存在！")
        return

    print("正在解析乐谱文件...")
    keys, delays = parse_score(file_path)
    if keys and delays:
        print(f"解析成功，共 {len(keys)} 个音符")
        print("5 秒后开始播放...")
        time.sleep(5)
        play_song(keys, delays)
    else:
        print("解析失败，请检查乐谱文件。")

if __name__ == "__main__":
    main()