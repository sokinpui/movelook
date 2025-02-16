from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
import os

api_key = os.environ['GENAI_API_KEY']

os.environ["GOOGLE_API_KEY"] = api_key

from langchain_google_genai import ChatGoogleGenerativeAI

model="gemini-1.5-flash-8b"
# Initialize the Gemini Pro model
llm = ChatGoogleGenerativeAI(model=model)

# Define the output schema
class Person(BaseModel):
    explanation: str = Field(description="explanation of the potential issue discovered in the log")
    linesNumber: list[str] = Field(description="lines of the log entries that contain the potential issue")


# Initialize the parser
parser = PydanticOutputParser(pydantic_object=Person)


# # Define the prompt template
# prompt = PromptTemplate(
#     template="Provide information about a person.\n{format_instructions}\n{query}",
#     input_variables=["query"],
#     partial_variables={"format_instructions": parser.get_format_instructions()},
# )


# Create the chain
# chain = (
#     {"query": RunnablePassthrough()}
#     | prompt
#     | llm
#     | parser
# )

# Example query
query = """
Dec 10 06:55:46 LabSZ sshd[24200]: reverse mapping checking getaddrinfo for ns.marryaldkfaczcz.com [173.234.31.186] failed - POSSIBLE BREAK-IN ATTEMPT!
Dec 10 06:55:46 LabSZ sshd[24200]: Invalid user webmaster from 173.234.31.186
Dec 10 06:55:46 LabSZ sshd[24200]: input_userauth_request: invalid user webmaster [preauth]
Dec 10 06:55:46 LabSZ sshd[24200]: pam_unix(sshd:auth): check pass; user unknown
Dec 10 06:55:46 LabSZ sshd[24200]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=173.234.31.186
Dec 10 06:55:48 LabSZ sshd[24200]: Failed password for invalid user webmaster from 173.234.31.186 port 38926 ssh2
Dec 10 06:55:48 LabSZ sshd[24200]: Connection closed by 173.234.31.186 [preauth]
Dec 10 07:02:47 LabSZ sshd[24203]: Connection closed by 212.47.254.145 [preauth]
Dec 10 07:07:38 LabSZ sshd[24206]: Invalid user test9 from 52.80.34.196
Dec 10 07:07:38 LabSZ sshd[24206]: input_userauth_request: invalid user test9 [preauth]
Dec 10 07:07:38 LabSZ sshd[24206]: pam_unix(sshd:auth): check pass; user unknown
Dec 10 07:07:38 LabSZ sshd[24206]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=ec2-52-80-34-196.cn-north-1.compute.amazonaws.com.cn
Dec 10 07:07:45 LabSZ sshd[24206]: Failed password for invalid user test9 from 52.80.34.196 port 36060 ssh2
Dec 10 07:07:45 LabSZ sshd[24206]: Received disconnect from 52.80.34.196: 11: Bye Bye [preauth]
Dec 10 07:08:28 LabSZ sshd[24208]: reverse mapping checking getaddrinfo for ns.marryaldkfaczcz.com [173.234.31.186] failed - POSSIBLE BREAK-IN ATTEMPT!
Dec 10 07:08:28 LabSZ sshd[24208]: Invalid user webmaster from 173.234.31.186
Dec 10 07:08:28 LabSZ sshd[24208]: input_userauth_request: invalid user webmaster [preauth]
Dec 10 07:08:28 LabSZ sshd[24208]: pam_unix(sshd:auth): check pass; user unknown
Dec 10 07:08:28 LabSZ sshd[24208]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=173.234.31.186
Dec 10 07:08:30 LabSZ sshd[24208]: Failed password for invalid user webmaster from 173.234.31.186 port 39257 ssh2
Dec 10 07:08:30 LabSZ sshd[24208]: Connection closed by 173.234.31.186 [preauth]
Dec 10 07:11:42 LabSZ sshd[24224]: Invalid user chen from 202.100.179.208
Dec 10 07:11:42 LabSZ sshd[24224]: input_userauth_request: invalid user chen [preauth]
Dec 10 07:11:42 LabSZ sshd[24224]: pam_unix(sshd:auth): check pass; user unknown
Dec 10 07:11:42 LabSZ sshd[24224]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=202.100.179.208
Dec 10 07:11:44 LabSZ sshd[24224]: Failed password for invalid user chen from 202.100.179.208 port 32484 ssh2
Dec 10 07:11:44 LabSZ sshd[24224]: Received disconnect from 202.100.179.208: 11: Bye Bye [preauth]
Dec 10 07:13:31 LabSZ sshd[24227]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=5.36.59.76.dynamic-dsl-ip.omantel.net.om  user=root
Dec 10 07:13:43 LabSZ sshd[24227]: Failed password for root from 5.36.59.76 port 42393 ssh2
Dec 10 07:13:56 LabSZ sshd[24227]: message repeated 5 times: [ Failed password for root from 5.36.59.76 port 42393 ssh2]
Dec 10 07:13:56 LabSZ sshd[24227]: Disconnecting: Too many authentication failures for root [preauth]
Dec 10 07:13:56 LabSZ sshd[24227]: PAM 5 more authentication failures; logname= uid=0 euid=0 tty=ssh ruser= rhost=5.36.59.76.dynamic-dsl-ip.omantel.net.om  user=root
Dec 10 07:13:56 LabSZ sshd[24227]: PAM service(sshd) ignoring max retries; 6 > 3
Dec 10 07:27:50 LabSZ sshd[24235]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:27:52 LabSZ sshd[24235]: Failed password for root from 112.95.230.3 port 45378 ssh2
Dec 10 07:27:52 LabSZ sshd[24235]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:27:53 LabSZ sshd[24237]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:27:55 LabSZ sshd[24237]: Failed password for root from 112.95.230.3 port 47068 ssh2
Dec 10 07:27:55 LabSZ sshd[24237]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:27:55 LabSZ sshd[24239]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:27:58 LabSZ sshd[24239]: Failed password for root from 112.95.230.3 port 49188 ssh2
Dec 10 07:27:58 LabSZ sshd[24239]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:27:58 LabSZ sshd[24241]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:00 LabSZ sshd[24241]: Failed password for root from 112.95.230.3 port 50999 ssh2
Dec 10 07:28:00 LabSZ sshd[24241]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:01 LabSZ sshd[24243]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:03 LabSZ sshd[24243]: Failed password for root from 112.95.230.3 port 52660 ssh2
Dec 10 07:28:03 LabSZ sshd[24243]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:03 LabSZ sshd[24245]: Invalid user pgadmin from 112.95.230.3
Dec 10 07:28:03 LabSZ sshd[24245]: input_userauth_request: invalid user pgadmin [preauth]
Dec 10 07:28:03 LabSZ sshd[24245]: pam_unix(sshd:auth): check pass; user unknown
Dec 10 07:28:03 LabSZ sshd[24245]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3
Dec 10 07:28:05 LabSZ sshd[24245]: Failed password for invalid user pgadmin from 112.95.230.3 port 54087 ssh2
Dec 10 07:28:05 LabSZ sshd[24245]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:06 LabSZ sshd[24247]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:08 LabSZ sshd[24247]: Failed password for root from 112.95.230.3 port 55618 ssh2
Dec 10 07:28:08 LabSZ sshd[24247]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:08 LabSZ sshd[24249]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:10 LabSZ sshd[24249]: Failed password for root from 112.95.230.3 port 57138 ssh2
Dec 10 07:28:10 LabSZ sshd[24249]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:10 LabSZ sshd[24251]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:12 LabSZ sshd[24251]: Failed password for root from 112.95.230.3 port 58304 ssh2
Dec 10 07:28:12 LabSZ sshd[24251]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:12 LabSZ sshd[24253]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:14 LabSZ sshd[24253]: Failed password for root from 112.95.230.3 port 59849 ssh2
Dec 10 07:28:14 LabSZ sshd[24253]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:14 LabSZ sshd[24255]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:16 LabSZ sshd[24255]: Failed password for root from 112.95.230.3 port 32977 ssh2
Dec 10 07:28:16 LabSZ sshd[24255]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:16 LabSZ sshd[24257]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:18 LabSZ sshd[24257]: Failed password for root from 112.95.230.3 port 35113 ssh2
Dec 10 07:28:18 LabSZ sshd[24257]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:19 LabSZ sshd[24259]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:21 LabSZ sshd[24259]: Failed password for root from 112.95.230.3 port 37035 ssh2
Dec 10 07:28:21 LabSZ sshd[24259]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:21 LabSZ sshd[24261]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:23 LabSZ sshd[24261]: Failed password for root from 112.95.230.3 port 39041 ssh2
Dec 10 07:28:23 LabSZ sshd[24261]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:23 LabSZ sshd[24263]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:25 LabSZ sshd[24263]: Failed password for root from 112.95.230.3 port 40388 ssh2
Dec 10 07:28:25 LabSZ sshd[24263]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:25 LabSZ sshd[24265]: Invalid user utsims from 112.95.230.3
Dec 10 07:28:25 LabSZ sshd[24265]: input_userauth_request: invalid user utsims [preauth]
Dec 10 07:28:25 LabSZ sshd[24265]: pam_unix(sshd:auth): check pass; user unknown
Dec 10 07:28:25 LabSZ sshd[24265]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3
Dec 10 07:28:28 LabSZ sshd[24265]: Failed password for invalid user utsims from 112.95.230.3 port 41506 ssh2
Dec 10 07:28:28 LabSZ sshd[24265]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:28 LabSZ sshd[24267]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:30 LabSZ sshd[24267]: Failed password for root from 112.95.230.3 port 42881 ssh2
Dec 10 07:28:30 LabSZ sshd[24267]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:31 LabSZ sshd[24269]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:33 LabSZ sshd[24269]: Failed password for root from 112.95.230.3 port 43981 ssh2
Dec 10 07:28:33 LabSZ sshd[24269]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:33 LabSZ sshd[24271]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:35 LabSZ sshd[24271]: Failed password for root from 112.95.230.3 port 44900 ssh2
Dec 10 07:28:35 LabSZ sshd[24271]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:35 LabSZ sshd[24273]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:37 LabSZ sshd[24273]: Failed password for root from 112.95.230.3 port 45699 ssh2
Dec 10 07:28:37 LabSZ sshd[24273]: Received disconnect from 112.95.230.3: 11: Bye Bye [preauth]
Dec 10 07:28:37 LabSZ sshd[24275]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=112.95.230.3  user=root
Dec 10 07:28:39 LabSZ sshd[24275]: Failed password for root from 112.95.230.3 port 46577 ssh2
"""

query = """
Given the follow log, please check if there contains any potential issues.

You should give a explanation of the potential issues and the lines related to this issue.
don't give any lines within the explanation.
only return lines if you think this line is related to the potential issues.
if you think there is no potential issues, don't return any lines.
""" + query

# Invoke the chain
# result = chain.invoke(query)

llm = llm.with_structured_output(Person)
result = llm.invoke(query)
print(result)
