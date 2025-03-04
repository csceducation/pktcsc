def global_context(request):
    return {
        "company": "Pudukottai",
        "user_ip": request.META.get("REMOTE_ADDR", "Unknown"),
    }
    
company = "Pudukottai"
site_pass = "622001"
uname = "pktcsc"