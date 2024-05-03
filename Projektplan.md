# Projektplan

## Entwurf in mermaid
Hilfe zur Syntax von mermaid ist hier:
https://mermaid.js.org/syntax/gantt.html

```mermaid
gantt
    
    dateFormat  DD.MM.YYYY
    axisFormat %d.%m
    tickInterval 1week
    weekday monday
    title       BibTexConverter
    excludes    weekends
    todayMarker stroke-width:5px,stroke:#0f0,opacity:0.5
    %% oder todayMarker off 
    
    
    section Orga-Milestones
        Gruppenbildung  :des1, 26.04.2024,  5d
        Fertigstellung Projektplan:       milestone, m2, 13.05.2024,
        Durchstich-Pitch : milestone, m5, 16.06.2024, 
        Abschlussdemo:     milestone, m10, 18.07.2024,
        %%Abgabe Dokumention:   milestone, m20, 30.09.2024,  
    
    
```










Hier ist ein Beispiel-Gantt-Chart in mermaid. Vielleicht können wir das benutzen.
```mermaid
gantt
    dateFormat  YYYY-MM-DD
    title       Adding GANTT diagram functionality to mermaid
    excludes    weekends
    %% (`excludes` accepts specific dates in YYYY-MM-DD format, days of the week ("sunday") or "weekends", but not the word "weekdays".)

    section A section
    Completed task            :done,    des1, 2014-01-06,2014-01-08
    Active task               :active,  des2, 2014-01-09, 3d
    Future task               :         des3, after des2, 5d
    Future task2              :         des4, after des3, 5d

    section Critical tasks
    Completed task in the critical line :crit, done, 2014-01-06,24h
    Implement parser and jison          :crit, done, after des1, 2d
    Create tests for parser             :crit, active, 3d
    Future task in critical line        :crit, 5d
    Create tests for renderer           :2d
    Add to mermaid                      :until isadded
    Functionality added                 :milestone, isadded, 2014-01-25, 0d

    section Documentation
    Describe gantt syntax               :active, a1, after des1, 3d
    Add gantt diagram to demo page      :after a1  , 20h
    Add another diagram to demo page    :doc1, after a1  , 48h

    section Last section
    Describe gantt syntax               :after doc1, 3d
    Add gantt diagram to demo page      :20h
    Add another diagram to demo page    :48h
```
