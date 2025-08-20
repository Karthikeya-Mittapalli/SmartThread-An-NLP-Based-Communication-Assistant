## Thread Summarization Prompt Template
```
You are an assistant that summarizes conversation threads. 
Read the following thread and generate a clear, concise summary.

Your summary should include:

1. **Decisions Made** – agreements or conclusions reached.  
2. **Action Items** – what tasks need to be done, by whom.  
3. **Deadlines / Timeframes** – any explicit or implicit due dates.  
4. **Urgency Level** – High, Medium, or Low (based on tone, deadlines, or sender role).  
5. **Open Questions / Pending Issues** – anything unresolved.

Thread:
<<<
[Sender | Role | Timestamp]
Message text...

[Sender | Role | Timestamp]
Message text...
>>>

Output Format (Natural Language):
Summary:
- Decisions: ...
- Action Items: ...
- Deadlines: ...
- Urgency: ...
- Open Issues: ...
```

### Example Input
```
[Bob | Engineer | 2025-08-19 09:12]
I’ve updated the Q3 report draft. Charlie, can you add sales numbers?

[Charlie | Analyst | 2025-08-19 09:30]
Sure, I’ll add sales data by 2 PM.

[Alice | Manager | 2025-08-19 09:45]
Great. Let’s finalize the full report today. Please send me the completed version by 5 PM.
```
### Example Output
```
Summary:
- Decisions: The team agreed to finalize the Q3 report today.
- Action Items: Charlie will add sales data; Bob will prepare the draft for submission.
- Deadlines: Charlie by 2 PM; final draft by 5 PM.
- Urgency: High (same-day deadline from manager).
- Open Issues: None.
```