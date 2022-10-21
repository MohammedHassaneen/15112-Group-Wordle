def acceptPendingRequests(dmHandler):
    """Accepts all the pending DM requests
    """
    pendingRequests=dmHandler.getPendingDMRequests()
    for pendingRequest in pendingRequests:
        dmHandler.approvePendingDMRequest(pendingRequest)