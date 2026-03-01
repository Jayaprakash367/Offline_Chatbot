# -*- coding: utf-8 -*-
"""Temporary script to write all Tamil data files. Delete after running."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────
# 1. intent_data.json
# ─────────────────────────────────────────────
intent_data = {
    "intents": [
        {
            "tag": "open_app",
            "patterns": [
                "open {app}", "launch {app}", "start {app}", "run {app}",
                "can you open {app}", "please open {app}",
                "{app} open pannu", "{app} tha", "{app} open podu",
                "{app} open pannunga", "{app} start pannu",
                "{app} launch pannu", "{app} run pannu",
                "{app} poduda", "{app} thora",
                "{app} திற", "{app} தொடு",
                "{app} ஓப்பன் பண்ணு",
                "{app} ஓபன் பண்ணு",
                "{app} ஸ்டார்ட் பண்ணு"
            ],
            "description": "User wants to open an application"
        },
        {
            "tag": "close_app",
            "patterns": [
                "close {app}", "shut down {app}", "exit {app}", "kill {app}", "stop {app}",
                "{app} close pannu", "{app} mooduda", "{app} nirthu",
                "{app} close pannunga", "{app} stop pannu",
                "{app} மூடு", "{app} நிறுத்து",
                "{app} க்ளோஸ் பண்ணு"
            ],
            "description": "User wants to close an application"
        },
        {
            "tag": "system_status",
            "patterns": [
                "system status", "cpu usage", "ram usage", "battery status", "battery level",
                "system health", "check system", "memory usage",
                "system status enna", "battery evvalavu", "cpu evvalavu",
                "system epdi irukku", "computer epdi irukku", "battery check pannu",
                "ram evvalavu use aaguthu", "cpu evvalavu use aaguthu",
                "பாட்டரி எவ்வளவு",
                "சிஸ்டம் எப்படி இருக்கு",
                "கம்ப்யூட்டர் எப்படி இருக்கு"
            ],
            "description": "User wants to check system health"
        },
        {
            "tag": "greeting",
            "patterns": [
                "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
                "vanakkam", "vaanga", "epdi irukeenga", "epdi irukkinga",
                "enna vishayam", "nallavara", "nalla irukeenga",
                "hi da", "hello da", "hey nanba",
                "வணக்கம்", "வாங்க",
                "எப்படி இருக்கீங்க",
                "நல்லா இருக்கீங்களா",
                "குட் மார்னிங்", "குட் ஆஃப்டர்நூன்", "குட் ஈவ்னிங்"
            ],
            "description": "User greets the AI"
        },
        {
            "tag": "farewell",
            "patterns": [
                "bye", "goodbye", "see you", "take care", "good night",
                "poi varean", "poi varen", "sari da", "bye da", "nandri",
                "poren", "pogattuma", "poi varuven",
                "போய் வரேன்", "போறேன்",
                "நன்றி", "பை பை"
            ],
            "description": "User says goodbye"
        },
        {
            "tag": "thanks",
            "patterns": [
                "thanks", "thank you", "thanks a lot",
                "nandri", "romba nandri", "thanks da", "thanks nanba",
                "nalla irukku", "super", "semma",
                "நன்றி", "ரொம்ப நன்றி",
                "நல்லா இருக்கு"
            ],
            "description": "User thanks the AI"
        },
        {
            "tag": "identity",
            "patterns": [
                "who are you", "what are you", "what is your name",
                "nee yaaru", "un peyar enna", "yaaru nee",
                "enna panra", "un name enna", "nee enna",
                "நீ யாரு", "உன் பேரு என்ன",
                "உன் பெயர் என்ன"
            ],
            "description": "User asks about the AI identity"
        },
        {
            "tag": "time",
            "patterns": [
                "what time is it", "current time", "tell me the time",
                "time enna", "mani enna", "eppa", "neram enna",
                "மணி என்ன", "நேரம் என்ன",
                "இப்போ என்ன டைம்"
            ],
            "description": "User asks for current time"
        },
        {
            "tag": "date",
            "patterns": [
                "what is the date", "today date", "current date",
                "innaiku enna date", "date enna", "innaiku enna",
                "enna thethi", "innaiku enna thethi",
                "இன்னைக்கு என்ன தேதி",
                "தேதி என்ன"
            ],
            "description": "User asks for current date"
        },
        {
            "tag": "joke",
            "patterns": [
                "tell me a joke", "say something funny", "make me laugh",
                "joke sollu", "comedy sollu", "oru joke sollu",
                "sirikka venum", "enna comedy", "funny ah sollu",
                "ஜோக் சொல்லு",
                "சிரிக்க வேணும்",
                "காமெடி சொல்லு"
            ],
            "description": "User wants a joke"
        },
        {
            "tag": "question",
            "patterns": [
                "what is {topic}", "tell me about {topic}", "explain {topic}",
                "{topic} enna", "{topic} pathi sollu", "{topic} explain pannu",
                "{topic} meaning enna", "{topic} ennadhaan",
                "{topic} என்ன", "{topic} பற்றி சொல்லு",
                "{topic} என்னன்னு சொல்லு"
            ],
            "description": "User asks a knowledge question"
        },
        {
            "tag": "teach",
            "patterns": [
                "let me teach you", "I want to teach you", "learn this", "remember this",
                "unakku katrukodukiren", "ithai learn pannu", "ithai remember pannu",
                "unakku sollikodukkiren", "kathu ko", "naan oru vishayam solren",
                "கற்றுக்கோ", "நெனப்படுத்துக்கோ",
                "இதை நினைவில் வை"
            ],
            "description": "User wants to teach the AI new knowledge"
        },
        {
            "tag": "help",
            "patterns": [
                "help", "help me", "what can you do",
                "enna panra sollu", "help pannu", "enna seiya mudiyum",
                "un abilities enna", "capabilities sollu",
                "உதவி செய்", "என்ன செய்ய முடியும்",
                "ஹெல்ப்"
            ],
            "description": "User asks for help"
        },
        {
            "tag": "name_set",
            "patterns": [
                "my name is", "call me", "I am",
                "en peyar", "ennai eppadi koopiduvathu", "naa",
                "என் பெயர்", "என்னை அழை"
            ],
            "description": "User provides their name"
        },
        {
            "tag": "mood_check",
            "patterns": [
                "how are you", "are you okay", "how do you feel",
                "nee epdi irukke", "nee santhoshamaa", "epdi irukke",
                "நீ எப்படி இருக்கே", "நீ சந்தோஷமா"
            ],
            "description": "User asks how the AI is doing"
        },
        {
            "tag": "unknown",
            "patterns": [],
            "description": "Fallback for unrecognized input"
        }
    ]
}

# ─────────────────────────────────────────────
# 2. emotion_data.json
# ─────────────────────────────────────────────
emotion_data = {
    "emotions": [
        {
            "emotion": "happy",
            "keywords": [
                "happy", "glad", "joy", "great", "wonderful", "excited", "awesome",
                "santhosham", "magizhchi", "semma", "super", "adipoli", "kalakku",
                "nalla irukku", "romba nalla", "mass", "theri", "vera level",
                "சந்தோஷம்", "மகிழ்ச்சி", "செம்ம", "சூப்பர்",
                "ஆடிபொலி", "களக்கு", "நல்லா இருக்கு",
                "வேற லெவல்", "மாஸ்"
            ],
            "phrases": [
                "i am happy", "feeling great", "so happy",
                "romba santhosham", "naan santhosham",
                "romba happy aa irukken", "semma feel",
                "ரொம்ப சந்தோஷம்", "நான் ஹாப்பி"
            ],
            "intensity": 1.0
        },
        {
            "emotion": "sad",
            "keywords": [
                "sad", "unhappy", "depressed", "down", "miserable", "upset", "cry",
                "sogam", "kavalai", "azhugiren", "kashtam", "baadha",
                "romba sogam", "varutham", "manasu valikkuthu",
                "சோகம்", "கவலை", "அழுகிறேன்", "கஷ்டம்",
                "பாதை", "வருத்தம்", "மனசு வலிக்குது"
            ],
            "phrases": [
                "i am sad", "feeling down", "so sad",
                "romba sogam aa irukku", "manasu valikkuthu",
                "kavalai aa irukku", "romba kashtam",
                "ரொம்ப சோகமா இருக்கு", "கவலையா இருக்கு"
            ],
            "intensity": 1.0
        },
        {
            "emotion": "angry",
            "keywords": [
                "angry", "furious", "mad", "irritated", "annoyed", "frustrated",
                "kovam", "eruchchal", "aaththiram", "porumai illa",
                "romba kovam", "sinna", "erichchu poguthu",
                "கோபம்", "எரிச்சல்", "ஆத்திரம்", "பொறுமை இல்ல",
                "சின்ன", "எரிச்சு போகுது"
            ],
            "phrases": [
                "i am angry", "so angry", "very mad",
                "romba kovam aa irukku", "aaththiram varuthu",
                "eruchchal aa irukku", "porumai illa",
                "ரொம்ப கோபமா இருக்கு", "எரிச்சலா இருக்கு"
            ],
            "intensity": 1.0
        },
        {
            "emotion": "fear",
            "keywords": [
                "scared", "afraid", "fear", "terrified", "anxious", "worried", "nervous",
                "bayam", "gabraappu", "tension", "payam", "kavalai",
                "romba bayam", "pattam", "nadunguthu",
                "பயம்", "கப்ராப்பு", "டென்ஷன்",
                "நடுங்குது", "கவலை"
            ],
            "phrases": [
                "i am scared", "so afraid", "very worried",
                "romba bayam aa irukku", "tension aa irukku",
                "payam aa irukku", "nadungi poguthu",
                "ரொம்ப பயமா இருக்கு", "டென்ஷனா இருக்கு"
            ],
            "intensity": 1.0
        },
        {
            "emotion": "neutral",
            "keywords": [
                "okay", "fine", "normal", "alright", "so so",
                "paravala", "ok", "sari", "adhuve dhaan", "podhum",
                "சரி", "பரவாலை", "ஓகே"
            ],
            "phrases": [
                "i am okay", "doing fine", "just normal",
                "paravala", "ok dhaan", "sari dhaan",
                "பரவாலை", "ஓகே தான்"
            ],
            "intensity": 0.3
        }
    ],
    "negation_words": [
        "not", "no", "never", "neither", "nobody", "nothing",
        "illa", "illai", "kidaiyaadhu", "mudiyaadhu",
        "இல்ல", "இல்லை", "கிடையாது", "முடியாது"
    ],
    "intensifiers": [
        "very", "really", "so", "extremely", "super", "too",
        "romba", "miga", "migavum", "rombave", "bayangara",
        "ரொம்ப", "மிக", "மிகவும்", "பயங்கர"
    ]
}

# ─────────────────────────────────────────────
# 3. responses.json
# ─────────────────────────────────────────────
responses_data = {
    "greeting": [
        "வணக்கம்! எப்படி இருக்கீங்க?",
        "வணக்கம்! நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        "ஹாய்! சொல்லுங்க, என்ன செய்யணும்?",
        "வாங்க வாங்க! என்ன விஷயம்?",
        "நமஸ்காரம்! சொல்லுங்க."
    ],
    "farewell": [
        "போய் வாங்க! பாதுகாப்பா இருங்க.",
        "சரி, மறுபடியும் வாங்க!",
        "பை பை! உங்கள் நாள் நல்லா இருக்கட்டும்.",
        "நன்றி! மீண்டும் சந்திப்போம்.",
        "போய்ட்டு வாங்க, நான் இங்க தான் இருக்கேன்."
    ],
    "thanks": [
        "பரவாலை, எப்பவும் உதவி செய்ய தயார்!",
        "நன்றி தேவையில்ல, இது என் வேலை!",
        "சந்தோஷம்! வேற ஏதாவது வேணுமா?",
        "உங்களுக்கு உதவி செய்வது எனக்கு மகிழ்ச்சி."
    ],
    "identity": [
        "நான் உங்கள் ஆஃப்லைன் AI உதவியாளர். நான் முழுவதும் உங்கள் கம்ப்யூட்டரில் வேலை செய்கிறேன்.",
        "நான் ஒரு AI assistant. இணையம் இல்லாமலே உங்களுக்கு உதவ முடியும்.",
        "என் பேரு AI Assistant. நான் உங்கள் கம்ப்யூட்டரில் ஆஃப்லைனில் வேலை செய்கிறேன்."
    ],
    "help": [
        "நான் பல விஷயங்கள் செய்ய முடியும்:\n- Apps திறக்க/மூட முடியும் (notepad, chrome, calculator)\n- System status பார்க்க முடியும் (CPU, RAM, Battery)\n- நேரம், தேதி சொல்ல முடியும்\n- ஜோக் சொல்ல முடியும்\n- உங்கள் உணர்வுகளை புரிந்துகொள்ள முடியும்\n- கேள்விகளுக்கு பதில் சொல்ல முடியும்",
        "சொல்லுங்க! App open/close, system check, jokes, Q&A - எல்லாம் செய்வேன்."
    ],
    "joke": [
        "ஒரு புரோகிராமர் ஏன் dark mode use பண்றாரு? ஏன்னா light bugs-ஐ attract பண்ணும்!",
        "Computer-க்கு cold ஆச்சு ஏன்? Windows open வச்சிருந்தாங்க!",
        "WiFi password என்ன? 'incorrect' - ஏன்னா எப்பவும் 'the password is incorrect' னு சொல்லும்!",
        "Programmer சாப்பாட்டுக்கு ஏன் போறதில்ல? ஏன்னா already full stack!",
        "Robot doctor கிட்ட போச்சு. Doctor: என்ன problem? Robot: Virus attack!"
    ],
    "time": [
        "இப்போது நேரம்: {time}",
        "இப்போ {time} ஆகுது.",
        "நேரம் {time}."
    ],
    "date": [
        "இன்னைக்கு தேதி: {date}",
        "இன்று {date}.",
        "தேதி: {date}."
    ],
    "open_app_success": [
        "{app} open ஆகிவிட்டது!",
        "{app} successfully திறக்கப்பட்டது.",
        "சரி, {app} open பண்ணிட்டேன்."
    ],
    "open_app_fail": [
        "மன்னிக்கவும், {app} open பண்ண முடியவில்ல.",
        "{app} திறக்க முடியல. App name சரியா இருக்கா check பண்ணுங்க.",
        "Sorry, {app} open ஆகல. Whitelisted app-ல இல்ல."
    ],
    "close_app_success": [
        "{app} close ஆகிவிட்டது.",
        "{app} மூடப்பட்டது.",
        "சரி, {app} close பண்ணிட்டேன்."
    ],
    "close_app_fail": [
        "{app} close பண்ண முடியல.",
        "மன்னிக்கவும், {app} இப்போ running-ல இல்ல.",
        "{app} மூட முடியல."
    ],
    "system_status": [
        "System Status:\n- CPU: {cpu}%\n- RAM: {ram}%\n- Battery: {battery}",
        "உங்கள் கம்ப்யூட்டர் நிலை:\nCPU பயன்பாடு: {cpu}%\nRAM பயன்பாடு: {ram}%\nBattery: {battery}"
    ],
    "emotion_response": {
        "happy": [
            "அருமை! நீங்க சந்தோஷமா இருக்கீங்கன்னு கேட்க மகிழ்ச்சி!",
            "செம்ம! உங்க சந்தோஷம் எனக்கும் சந்தோஷம்!",
            "சூப்பர்! இந்த mood-ல continue பண்ணுங்க!"
        ],
        "sad": [
            "கவலைப்படாதீங்க, எல்லாம் நல்லா ஆகும்.",
            "நான் உங்க கூட இருக்கேன். என்ன help வேணும்?",
            "வருத்தமா இருக்கா? ஒரு ஜோக் சொல்லட்டுமா?"
        ],
        "angry": [
            "ஆறுதலா இருங்க. கோபத்துல முடிவு எடுக்காதீங்க.",
            "புரியுது. Take a deep breath.",
            "கோபம் கொஞ்சம் குறையட்டும். நான் இருக்கேன்."
        ],
        "fear": [
            "பயப்படாதீங்க, நான் இருக்கேன்.",
            "Tension வேண்டாம், relax பண்ணுங்க.",
            "கவலை வேண்டாம். எல்லாம் சரியாகும்."
        ],
        "neutral": [
            "சரி, என்ன செய்யணும் சொல்லுங்க.",
            "ஓகே, உங்களுக்கு எப்படி உதவ முடியும்?",
            "சொல்லுங்க, கேக்குறேன்."
        ]
    },
    "teach_prompt": [
        "சொல்லுங்க, என்ன கற்றுக்கணும்? 'question | answer' format-ல சொல்லுங்க.",
        "புதுசா கற்றுக்க ரெடி! question | answer format-ல type பண்ணுங்க."
    ],
    "teach_success": [
        "நன்றி! கற்றுக்கிட்டேன்!",
        "புரிஞ்சுது, நினைவில் வச்சுக்கிட்டேன்!",
        "சரி, இதை remember பண்ணிட்டேன்."
    ],
    "unknown": [
        "மன்னிக்கவும், எனக்கு புரியல. வேற மாதிரி சொல்லுங்க.",
        "இது என் தெரிவுக்கு அப்பாற்பட்டது. வேற question கேளுங்க.",
        "புரியல. 'help' னு type பண்ணி என்ன செய்ய முடியும்னு பாருங்க.",
        "Sorry, புரியல. தமிழ்ல அல்லது English-ல try பண்ணுங்க."
    ],
    "name_set": [
        "வணக்கம் {name}! உங்களை சந்திக்க மகிழ்ச்சி!",
        "ஹாய் {name}! நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        "நல்லது {name}, உங்கள் பெயர் நினைவில் வைத்துக்கிறேன்."
    ],
    "mood_check": [
        "நான் நல்லா இருக்கேன், நன்றி! நீங்க எப்படி இருக்கீங்க?",
        "எனக்கு எப்பவும் நல்லா தான் இருக்கும்! சொல்லுங்க.",
        "நான் fine! உங்களுக்கு என்ன help வேணும்?"
    ],
    "safety_block": [
        "மன்னிக்கவும், இந்த command-ஐ run பண்ண முடியாது. Safety reasons.",
        "இது அனுமதிக்கப்பட்ட command இல்ல.",
        "பாதுகாப்பு காரணமா இது block ஆகிவிட்டது."
    ]
}

# ─────────────────────────────────────────────
# 4. knowledge_base.json
# ─────────────────────────────────────────────
knowledge_data = {
    "entries": [
        {
            "question": "python என்ன",
            "answer": "Python ஒரு high-level programming language. இது எளிமையானது, படிக்க எளிது, web development, AI, data science போன்ற பல துறைகளில் பயன்படுகிறது.",
            "tags": ["python", "programming", "language", "புரோகிராமிங்"]
        },
        {
            "question": "AI என்ன",
            "answer": "AI (Artificial Intelligence) என்பது கம்ப்யூட்டர்கள் மனிதர்களைப் போல சிந்திக்கவும் கற்றுக்கொள்ளவும் உதவும் தொழில்நுட்பம்.",
            "tags": ["ai", "artificial intelligence", "செயற்கை நுண்ணறிவு"]
        },
        {
            "question": "machine learning என்ன",
            "answer": "Machine Learning என்பது AI-யின் ஒரு பிரிவு. இதில் கம்ப்யூட்டர்கள் data-வில் இருந்து தானாகவே கற்றுக்கொள்ளும்.",
            "tags": ["machine learning", "ml", "இயந்திர கற்றல்"]
        },
        {
            "question": "operating system என்ன",
            "answer": "Operating System (OS) என்பது கம்ப்யூட்டர் hardware-ஐ நிர்வகிக்கும் software. Windows, Linux, macOS ஆகியவை examples.",
            "tags": ["os", "operating system", "இயக்க முறைமை"]
        },
        {
            "question": "internet என்ன",
            "answer": "Internet என்பது உலகம் முழுவதும் கம்ப்யூட்டர்களை இணைக்கும் ஒரு global network. இது தகவல்களை பகிர்ந்து கொள்ள உதவுகிறது.",
            "tags": ["internet", "network", "இணையம்"]
        },
        {
            "question": "cloud computing என்ன",
            "answer": "Cloud Computing என்பது internet மூலம் storage, servers, databases போன்ற computing services-ஐ provide செய்வது.",
            "tags": ["cloud", "computing", "கிளவுட்"]
        },
        {
            "question": "cybersecurity என்ன",
            "answer": "Cybersecurity என்பது கம்ப்யூட்டர் systems, networks, data-வை தாக்குதல்களில் இருந்து பாதுகாப்பது.",
            "tags": ["cybersecurity", "security", "இணைய பாதுகாப்பு"]
        },
        {
            "question": "database என்ன",
            "answer": "Database என்பது organized data collection. MySQL, PostgreSQL, MongoDB போன்றவை popular databases.",
            "tags": ["database", "db", "தரவுத்தளம்"]
        },
        {
            "question": "algorithm என்ன",
            "answer": "Algorithm என்பது ஒரு problem-ஐ solve செய்ய step-by-step instructions. Sorting, searching போன்றவை common algorithms.",
            "tags": ["algorithm", "அல்காரிதம்"]
        },
        {
            "question": "html என்ன",
            "answer": "HTML (HyperText Markup Language) என்பது web pages-ஐ உருவாக்க பயன்படும் standard markup language.",
            "tags": ["html", "web", "வலைப்பக்கம்"]
        },
        {
            "question": "compiler என்ன",
            "answer": "Compiler என்பது high-level programming language code-ஐ machine code-ஆக மாற்றும் program.",
            "tags": ["compiler", "programming", "கம்பைலர்"]
        },
        {
            "question": "RAM என்ன",
            "answer": "RAM (Random Access Memory) என்பது கம்ப்யூட்டரின் temporary memory. இது currently running programs-க்கு data store செய்கிறது.",
            "tags": ["ram", "memory", "நினைவகம்"]
        },
        {
            "question": "CPU என்ன",
            "answer": "CPU (Central Processing Unit) என்பது கம்ப்யூட்டரின் 'மூளை'. இது எல்லா calculations-ஐயும் process செய்கிறது.",
            "tags": ["cpu", "processor", "செயலி"]
        },
        {
            "question": "virus என்ன",
            "answer": "Computer virus என்பது ஒரு malicious program. இது கம்ப்யூட்டர்களுக்கு damage செய்யும் மற்றும் spread ஆகும்.",
            "tags": ["virus", "malware", "வைரஸ்"]
        },
        {
            "question": "API என்ன",
            "answer": "API (Application Programming Interface) என்பது இரண்டு software applications communicate செய்ய உதவும் interface.",
            "tags": ["api", "interface", "ஏபிஐ"]
        },
        {
            "question": "git என்ன",
            "answer": "Git என்பது ஒரு version control system. இது code changes-ஐ track செய்யவும் team-ஆக collaborate செய்யவும் உதவுகிறது.",
            "tags": ["git", "version control", "கிட்"]
        },
        {
            "question": "deep learning என்ன",
            "answer": "Deep Learning என்பது machine learning-ன் ஒரு subset. இது neural networks பயன்படுத்தி complex patterns-ஐ கற்றுக்கொள்ளும்.",
            "tags": ["deep learning", "neural network", "ஆழ்கற்றல்"]
        },
        {
            "question": "தமிழ் என்ன",
            "answer": "தமிழ் உலகின் மிகப்பழமையான மொழிகளில் ஒன்று. இது 2000+ வருடங்கள் பழமையானது. தமிழ்நாடு, இலங்கை, சிங்கப்பூர் போன்ற இடங்களில் பேசப்படுகிறது.",
            "tags": ["tamil", "language", "தமிழ்", "மொழி"]
        },
        {
            "question": "திருக்குறள் என்ன",
            "answer": "திருக்குறள் திருவள்ளுவர் எழுதிய அறநூல். இது 1330 குறள்களைக் கொண்டது. அறம், பொருள், இன்பம் என்ற 3 பிரிவுகளை உள்ளடக்கியது.",
            "tags": ["thirukkural", "thirukural", "திருக்குறள்", "வள்ளுவர்"]
        },
        {
            "question": "bharathiyar யார்",
            "answer": "சுப்ரமணிய பாரதியார் ஒரு புகழ்பெற்ற தமிழ் கவிஞர். இந்திய சுதந்திர இயக்கத்தில் பங்கேற்றவர். 'வந்தே மாதரம்' போன்ற பாடல்கள் எழுதினார்.",
            "tags": ["bharathiyar", "poet", "பாரதியார்", "கவிஞர்"]
        }
    ]
}

# ─────────────────────────────────────────────
# Write all files
# ─────────────────────────────────────────────
data_dir = os.path.join(BASE, "data")

with open(os.path.join(data_dir, "intent_data.json"), "w", encoding="utf-8") as f:
    json.dump(intent_data, f, indent=4, ensure_ascii=False)
print("[OK] intent_data.json")

with open(os.path.join(data_dir, "emotion_data.json"), "w", encoding="utf-8") as f:
    json.dump(emotion_data, f, indent=4, ensure_ascii=False)
print("[OK] emotion_data.json")

with open(os.path.join(data_dir, "responses.json"), "w", encoding="utf-8") as f:
    json.dump(responses_data, f, indent=4, ensure_ascii=False)
print("[OK] responses.json")

with open(os.path.join(data_dir, "knowledge_base.json"), "w", encoding="utf-8") as f:
    json.dump(knowledge_data, f, indent=4, ensure_ascii=False)
print("[OK] knowledge_base.json")

print("\nAll 4 Tamil data files written successfully!")
