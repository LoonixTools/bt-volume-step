PREFIX  ?= /usr
DESTDIR ?=

BINDIR  = $(DESTDIR)$(PREFIX)/bin
UNITDIR = $(DESTDIR)$(PREFIX)/lib/systemd/user

.PHONY: install uninstall check

install:
	install -Dm755 bt-volume-step $(BINDIR)/bt-volume-step
	install -Dm644 systemd/bt-volume-step.service \
		$(UNITDIR)/bt-volume-step.service
	sed -i 's|^ExecStart=.*|ExecStart=$(PREFIX)/bin/bt-volume-step|' \
		$(UNITDIR)/bt-volume-step.service

uninstall:
	rm -f $(BINDIR)/bt-volume-step
	rm -f $(UNITDIR)/bt-volume-step.service

check:
	python3 tests/test_bt_volume_step.py
