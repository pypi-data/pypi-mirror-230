SERVICE_CONFIG = """
[Unit]
Description=knivesout daemon
After=multi-user.target

[Service]
WorkingDirectory=/tmp/
ExecStart={}
Restart=always

[Install]
WantedBy=multi-user.target
"""