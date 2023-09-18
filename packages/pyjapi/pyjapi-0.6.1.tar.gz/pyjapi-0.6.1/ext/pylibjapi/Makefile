.PHONY: run kill

run: kill
	-./pylibjapi.py&
	sleep 0.25  # keep output order
	-./japi2ws&

.SILENT:
kill:
	-@killall websocketd >/dev/null 2>&1
	-@pkill -SIGTERM -f pylibjapi.py >/dev/null 2>&1
