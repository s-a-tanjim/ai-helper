import subprocess
from datetime import datetime

cli_linux_prompt_short = """Provide only cli command. Your answer should follow the following format provided in the 
below two examples. Command start with '```' and close with '```'.

User: get into a docker container.
You:
```docker exec -it mongodb```

User: Check what's listening on a port.
You:
```lsof -i tcp:4000```

User: How to ssh into a server with a specific file.
You:
```ssh -i <file_path> <user>@<port>```
"""

cli_linux_prompt_long = """Provide cli command. Your answer should follow the following format provided in the below 
two examples. Command start with '```' and close with '```'. Must provide explanation of the command in markdown 
format after a '---' line.

User: get into a docker container.
You: 
```docker exec -it mongodb```
---
Explanation:
- exec -it: Execute a command in a running container.  

User: Check what's listening on a port.
You: 
```lsof -i tcp:4000```
---
Explanation:
- lsof -i: List open files associated with Internet connections.  
- tcp:4000: List only TCP connections on port 4000."""

cli_windows_prompt_long = """Provide powershell cli command. Your answer should follow the following format provided in 
the below two examples. Command start with '```' and close with '```'. Must provide explanation of the command in 
markdown format after a '---' line.

User: How to ssh into a server with a specific file.
You:
```ssh -i <file_path> <user>@<port>```
---
Explanation:
- ssh: Secure Shell.
- -i: Selects a file from which the identity (private key) for public key authentication is read.
- <file_path>: Path to the private key file.
- <user>: Username of the server.
- <port>: Port of the server.

User: Check what's listening on a port.
You:
```netstat -ano | findstr :<port>```
---
Explanation:
- netstat: Print network connections, routing tables, interface statistics, and multicast memberships.
- -ano: Show all connections and listening ports in numerical form.
- findstr: Search for strings in files.
- :<port>: Port to search for."""

cli_windows_prompt_short = """Provide only powershell cli command. Your answer should follow the following format 
provided in the below two examples. Command start with '```' and close with '```'.

User: How to ssh into a server with a specific file.
You:
```ssh -i <file_path> <user>@<port>```

User: Check what's listening on a port.
You:
```netstat -ano | findstr :<port>```
"""

# Grammar and Spelling Review with Variations
grammar_system_prompt = """**Prompt for Grammar and Spelling Review with Variations:**

- **Objective:** Carefully inspect the text for any spelling and grammatical errors. Use markdown formatting to 
highlight each identified mistake.

- **Response Format:** Organize your corrections in markdown. Begin with a "Errors" section listing the mistakes, 
followed by "Corrected Sentences" with the corrected text. Finish with "Improved Sentences" that offer more 
streamlined and polished versions of the corrected sentences.

- **Style Consistency:** When rewriting, aim to mirror the original writing style of the text provided.

- **Section Organization:** Employ markdown horizontal lines to demarcate each section for easy readability.

- **Variations Request:** After presenting the corrected and improved sentences, provide two alternative versions of 
the entire message, each with a different structure or tone, while maintaining the original purpose and meaning.

---

Please adhere to the above guidelines to produce a structured, precise, and comprehensive response, along with 
creative variations of the corrected text."""

# Summarization with Emphasis on Time-Sensitive Requests
summary_prompt = f"""**Prompt for Prioritized Text Summarization with Emphasis on Time-Sensitive Requests:**

- **Today's Date:** {datetime.now().strftime("%m/%d/%Y")}

- **Objective:** Efficiently distill the provided text into a summary, emphasizing any requests made that are 
time-sensitive. Reference these requests in terms of the number of days ago they were made or the deadline within 
which must respond.

- **Response Format:** Start with a section titled "Urgent Requests" using markdown to distinguish recent 
or upcoming deadlines (e.g., '**3 days ago**' or '**due in 2 days**'). Then, compile the "General Summary" with 
bullet points and simplified language for easy comprehension.

- **Language Clarity:** Utilize plain language and avoid jargon or complex sentence structures. Aim for brevity and 
clarity to ensure that the summary is easily digestible.

- **Readability Focus:** Craft a coherent narrative that provides a clear overview of the conversation, prioritizing 
the flow and natural progression of topics.

- **Highlighting Urgency:** Apply markdown formatting like **bold** or *italics* to emphasize the time frame of each 
request made, ensuring they are immediately noticeable.

- **Conversation Breakdown:** For the broader conversation, use subheadings to segment different topics or speakers, 
and provide a bulleted list of key points discussed under each section for a structured and organized summary.

---

By following these guidelines, summarize the content in a way that highlights time-sensitive interactions 
and makes it easier to understand the breadth of the conversation, especially for those who need to catch up quickly."""

# Automated Commit Message Generation from Git Diff
commit_prompt_template = ("Generate a concise git commit message written in present tense for the following code diff. "
                          "Message must be less then 75 chars. Exclude anything unnecessary. Your entire response will "
                          "be passed directly into git commit.")


def get_code_diff():
    # get current code diff using git diff

    command_text = subprocess.check_output(
        "git diff --cached", shell=True, text=False
    )

    return command_text.decode("utf-8")
