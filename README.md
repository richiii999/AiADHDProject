
# **FOCUS**: An Agentic AI Framework for Helping ADHD Students Learn More Effectively

**Motivation** ADHD: Approximately 7 million U.S students 
(1 in 9) have Attention Deficit and Hyperactivity Disorder (ADHD), impacting their academic performance, leading to a life of learning struggles and low economic mobility.

Need for Adaptive Solutions: Software does exist to help ADHD students to stay focused and learn effectively. However, ADHD has 3 different profiles, each with distinct symptoms and requiring different accommodations for learning effectively. Besides, people in general have different ways of learning (VARK model). All this to say, existing software for ADHD students fails to dynamically adjust to individual students’ features sufficiently.

**FOCUS Overview** FOCUS: an Agentic AI-empowered solution:
Perception - Active monitoring to detect distractions via sensors.
Reasoning - local SLM / Cloud LLM models .
Action - Users are automatically given suggestions from a range of possible actions, informed by an expert knowledge-base.
Memory - User study behaviors are learned by the AI to provide personalized recommendations.

**Research Challenges**
RQ1: How to adopt the emerging agentic AI paradigm to help with ADHD?

RQ2: how to make the solution adaptive, extensible, and personalizable? 

RQ3: understanding the performance of the proposed solution in various user scenarios, such as the 3 main ADHD profiles?

**FOCUS Design and Implementation** FOCUS is designed as a conversational study assistant: it follows the Agentic AI paradigm by 1) perceiving the user via sensors like cameras, mouse and keyboard inputs, microphone, screen monitoring, 2) reasoning about learner’s real-time status, learning barriers, and their study patterns based on these input as well as other information from a knowledge base, and 3) preempting them from being distracted by offering actions that allow the user to be better engaged with the material they are studying. 4) Learning the user's study patterns by repeatedly interacting with the learner and observing how effective these actions are, thus improving the effectiveness of actions over time (RQ1). 

For example, say that by eye tracking, FOCUS detects the learner is 'zoned out' for an extended period of time and prompts the user with, say, a quiz. After repeated sessions, FOCUS learns that the learner’s attention span is typically 20 minutes, and would suggest a break when close to this limit (RQ2-personalized). Another example would be that a user is looking away from the computer screen for an extended amount of time, then it would prompt the student to take one of several actions to reduce their distractions, such as taking a break.

FOCUS is designed to be a modular framework, where each component (see diagram) is loosely coupled and can be changed without any specific integration. In such a way, it can easily adapt to different setups while incorporating expert knowledge and learning material (RQ2- Adaptive and Extensible). 

We implemented FOCUS using OpenWebUI, an agentic AI platform for model serving and tool integration. OpenCV was used for face and gaze tracking via webcam input, and a local Visual Language Model (VLM) identified the content read by the learner. Prompts and retrieval-augmented generation (RAG) provided relevant context to one of a variety of reasoning model(s) tailored to learners’ cost and accuracy needs. The chosen reasoning model also summarizes each study session and maintains a long-term learner profile. While further testing with a cohort of ADHD students is planned (RQ3), initial results show that FOCUS effectively learned simulated learning patterns and increasingly suggested more effective actions over repeated sessions.

**FOCUS Workflow** (todo image)

**References** (Zotero Library)

**Project Code** (Github Repo)

**Requirements**
- Python 3.x
- OpenCV (opencv-python)
- MediaPipe (mediapipe)
- list stuff

**Installation & Usage**

1. **Clone the Repository:**
   ```
   git clone https://github.com/alireza787b/Python-Gaze-Face-Tracker.git
   ```

2. **Navigate to the Repository Directory:**
   ```
   cd Python-Gaze-Face-Tracker
   ```

3. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```
   python main.py
   ```

   Optionally, specify the camera source:
   ```
   python main.py -c <camera_source_number>
   ```

5. **Open in VS Code:**
   ```
   code .
   ```
      Optionally, open the project in VS Code:

**Acknowledgements** This research was conducted as part of the SURE program at UMD, which is paid (todo copy their ack here)