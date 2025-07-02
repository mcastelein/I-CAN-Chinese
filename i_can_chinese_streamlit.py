import streamlit as st
import streamlit.components.v1 as components
from pydub import AudioSegment
import random
import os

st.set_page_config(page_title="I CAN Chinese", layout="wide")
st.title("I CAN Chinese")

# User-controlled pause duration in seconds (default: 2)
pause_seconds = st.slider("⏸️ Pause between English and Chinese (seconds)", min_value=0.0, max_value=5.0, value=2.0, step=0.5)
# Display toggles
show_chinese = st.checkbox("Show Chinese (Characters)", value=False)
show_pinyin = st.checkbox("Show Chinese (Pinyin)", value=False)



def get_word_list(section_path):
    english_folder = os.path.join("Audio_Files", section_path, "English")
    mp3_files = [f for f in os.listdir(english_folder) if f.endswith(".mp3")]

    def extract_sort_key(filename):
        name = os.path.splitext(filename)[0]
        parts = name.split("_", 1)
        return int(parts[0]) if len(parts) == 2 and parts[0].isdigit() else float("inf")

    mp3_files.sort(key=extract_sort_key)
    words = [os.path.splitext(f)[0] for f in mp3_files]
    return words


def generate_combined_audio(word_list, section, repeat=5, pause_ms=2000):
    combined = AudioSegment.silent(duration=0)
    # Detect if any of the words have a numeric prefix → disable shuffle
    for i in range(repeat):
        if i == 0:
            word_order = word_list  # First pass: original order
        else:
            word_order = word_list.copy()
            random.shuffle(word_order)  # Subsequent passes: shuffled

        for word in word_order:
            en_path = f"Audio_Files/{section}/English/{word}.mp3"
            zh_path = f"Audio_Files/{section}/Chinese/{word}.mp3"

            en_audio = AudioSegment.from_mp3(en_path)
            zh_audio = AudioSegment.from_mp3(zh_path)

            combined += en_audio
            combined += AudioSegment.silent(duration=pause_ms)
            combined += zh_audio
            combined += AudioSegment.silent(duration=1000)


    output_path = "temp_output.mp3"
    combined.export(output_path, format="mp3")
    return output_path



def audio_section(section):
    toggle_key = f"show_section_{section}"

    if toggle_key not in st.session_state:
        st.session_state[toggle_key] = False

    if st.button(f"🔽 {section}" if not st.session_state[toggle_key] else f"🔼 Hide {section}"):
        st.session_state[toggle_key] = not st.session_state[toggle_key]

    if st.session_state[toggle_key]:
        words = get_word_list(section)
        # Load Chinese + Pinyin info from Info.txt
        info_map = {}
        info_path = os.path.join("Audio_Files", section, "Info.txt")
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        word_id, zh, py = parts[0].replace("_", " "), parts[1], parts[2]
                        info_map[word_id] = {"zh": zh, "pinyin": py}
                    elif len(parts) == 2:
                        word_id, zh = parts[0].replace("_", " "), parts[1]
                        info_map[word_id] = {"zh": zh, "pinyin": ""}


        selected_words = []

        # Layout checkboxes in rows of 5
        cols = st.columns(5)
        for idx, word in enumerate(words):
            col = cols[idx % 5]
            with col:
                key = f"learned_{section}_{word}"
                if key not in st.session_state:
                    st.session_state[key] = True
                base_word = word.split("_", 1)[-1]
                zh_word = info_map.get(word, {}).get("zh", "")
                pinyin = info_map.get(word, {}).get("pinyin", "")

                parts = [base_word]
                if show_chinese and zh_word:
                    parts.append(zh_word)
                if show_pinyin and pinyin:
                    parts.append(f"{pinyin}")

                full_label = " - ".join(parts)

                with col:
                    st.checkbox("", key=key)
                    st.write(full_label)
                    if st.session_state[key]:
                        selected_words.append(word)



        centered_cols = st.columns([2, 1, 2])  # Left, center, right columns
        with centered_cols[1]:
            if st.button(f"▶️ Play {section} Audio"):
                if selected_words:
                    audio_file = generate_combined_audio(selected_words, section, pause_ms=int(pause_seconds * 1000))
                    st.audio(audio_file, format="audio/mp3")
                else:
                    st.warning("Please select at least one word.")


section_list = [
    "1. Fruits",
    "2. Food & Drinks",
    "3. Vegetables",
    "4. Greetings",
    "5. Family",
    "6. Fruits 1",
    "7. Fruits 2",
    "8. Family",
    "9. Numbers 1",
    "10. Numbers 2",
    "11. Body Parts",
    "12. Colors",
    "13. Clothing",
    "14. Verbs 1",
    "15. Verbs 2",
    "16. Shopping",
    "17. CCP Values",
    "18. Math Terms",
    "19. Nature",
    "20. Table Tennis 1",
    "21. Table Tennis 2",
    "22. Table Tennis 3",
    "23. Countries",
    "24. Sports",
    "25. Personality Traits",
    "26. Furniture",
    "27. Rooms",
    "28. Weather",
    "29. Transportation",
    "30. Hobbies"
]


for section in section_list:
    audio_section(section)  

