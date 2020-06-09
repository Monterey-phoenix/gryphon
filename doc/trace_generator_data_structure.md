Trace generator data structure from JSON, see JSON_file_structure.pdf

    data_structure={"traces":[trace,...],
                    "GLOBAL":global_view}
    
    trace=[
    
        # [0] MARK_flag: Unmarked or Marked
        "U" or "M"
    
        # [1] trace probability
        int
    
        # [2] event list
        [event_descriptor,...],
    
            event_descriptor=[
    
                # event_name
                str
    
                # event_type: atomic, composite, root, schema, Say message
                "A", "C", "R", "S", or "T"
    
                # event ID
                int
    
                # layout_column_number
                int
    
                # layout_row_number
                int
    
        # [3] IN_relation_list
        [[event_id int, event_id int], ...] # a IN b
    
        # [4] FOLLOWS_relation_list
        [[event_id int, event_id int], ...] # a FOLLOWS b
    
        # [5..n-1] user_defined_relation_elements
        <relation_name>, [event_id int, event_id int] # a relation b
        ...
    
        # [n] views
        "VIEWS":[view_object, ...?]
    
        view_object={
          "REPORT":["<title>", "line1", "line2", "..."]
          "GRAPH":["<title>", node list, arrow list, line list] # fill in later.
          "BAR_CHART":[...] # not documented
          "GANTT_CHART":[...] # not documented
          "AD":["<title>", node descriptor, arrow list]] # not fully documented
        }
    
    # GLOBAL
    global_view=[MARK_flag U/M,
    
                 # SAY_messages
                 {"SAY":["text","text","..."]}
    
                 # view_object
                 {<view_object, see above>}
