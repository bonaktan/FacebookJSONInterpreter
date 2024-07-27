# Server Architecture
To make it atleast slightly faster, use of multiprocessing capabilities will be required.
API and Backend will run on seperate cores.

# Terminologies
|Term|Meaning|
|---|---|
|Media|Files that are not .json (usually photos, videos, generic files, etc.)
|Data|A .json (or collection of it)|
|Conversation|A special collection of Data|
|ConvoMessage|A snippet of a conversation|
## API-Side


## Backend
### Data Structure
#### FacebookData
- your_facebook_data/* is represented
#### FacebookData.Metadata
- everything else in root (except your_facebook_data) is represented