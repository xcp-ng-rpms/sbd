#
# spec file for package sbd
#
# Copyright (c) 2014 SUSE LINUX Products GmbH, Nuernberg, Germany.
# Copyright (c) 2013 Lars Marowsky-Bree
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#
%global commit a74b4d25a3eb93fe1abbe6e3ebfd2b16cf48873f
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global github_owner Clusterlabs
%global buildnum 7

Name:           sbd
Summary:        Storage-based death
License:        GPLv2+
Group:          System Environment/Daemons
Version:        1.3.1
Release:        7.xs+2.0.0%{?dist}
Url:            https://github.com/%{github_owner}/%{name}
#Source0:        https://github.com/%{github_owner}/%{name}/archive/%{commit}/%{name}-%{commit}.tar.gz

Source0: https://code.citrite.net/rest/archive/latest/projects/XSU/repos/sbd/archive?at=a74b4d25a3eb93fe1abbe6e3ebfd2b16cf48873f&format=tar.gz&prefix=sbd-a74b4d25a3eb93fe1abbe6e3ebfd2b16cf48873f#/sbd-a74b4d25a3eb93fe1abbe6e3ebfd2b16cf48873f.tar.gz
Patch0: SOURCES/sbd/0001-make-pacemaker-dlm-wait-for-sbd-start.patch
Patch1: SOURCES/sbd/0002-mention-timeout-caveat-with-SBD_DELAY_START.patch
Patch2: SOURCES/sbd/0003-Doc-sbd.8.pod-add-query-test-watchdog.patch

Patch3: 0001-Tweak-sbd-inquisitor.c-to-retain-the-same-behaviour-.patch
Patch4: 0001-sbd-cluster-only-report-good-health-if-quorate-or-no.patch
Patch5: 0002-increase_logging_level_to_CRIT_for_quorum_loss.patch
Patch6: CA-290057__barebones_Xapi_sbd_servant
Patch7: CA-290057__call_xapi-health-check_from_thread_and_set_servant_status_appropriately
Patch8: CA-290057__fix_compilation_warnings
Patch9: CA-292257__log_xapi_checker_failures_at_LOG_ERR
Patch10: CA-292257__sbd_xapi_servant_outdated
Patch11: CA-290600__Xapi_SBD_watcher_segfault

Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XSU/repos/sbd.centos/archive?at=imports%2Fc7%2Fsbd-1.3.1-7.el7&format=tar.gz#/sbd-1.3.1.centos.tar.gz) = e38fd2356724512cb5a98add1fb973d86615de6e
Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XSU/repos/sbd/archive?at=a74b4d25a3eb93fe1abbe6e3ebfd2b16cf48873f&format=tar.gz&prefix=sbd-a74b4d25a3eb93fe1abbe6e3ebfd2b16cf48873f#/sbd-a74b4d25a3eb93fe1abbe6e3ebfd2b16cf48873f.tar.gz) = a74b4d25a3eb93fe1abbe6e3ebfd2b16cf48873f
Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XS/repos/sbd.pg/archive?at=2.0.0&format=tar#/sbd-2.0.0.pg.tar) = 6a6f4c579419a7c28c8b6e5bf5f7ad1f5960f3a5

BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libuuid-devel
BuildRequires:  glib2-devel
BuildRequires:  libaio-devel
BuildRequires:  corosync-devel
BuildRequires:  xenserver-corosync
BuildRequires:  xenserver-pacemaker-libs-devel > 1.1.12
BuildRequires:  libtool
BuildRequires:  libuuid-devel
BuildRequires:  libxml2-devel
BuildRequires:  pkgconfig
BuildRequires:  python-devel
BuildRequires:  git

%if 0%{?rhel} > 0
ExclusiveArch: i686 x86_64 s390x ppc64le
%endif

%if %{defined systemd_requires}
%systemd_requires
%endif

Provides: xenserver-%{name}

%description

This package contains the storage-based death functionality.

###########################################################

%prep
%autosetup -n %{name}-%{commit} -p1 -S git

###########################################################

%build
autoreconf -i
export CFLAGS="$RPM_OPT_FLAGS -Wall -Werror"
%configure
make %{?_smp_mflags}

###########################################################

%install

make DESTDIR=$RPM_BUILD_ROOT LIBDIR=%{_libdir} install
rm -rf ${RPM_BUILD_ROOT}%{_libdir}/stonith

%if %{defined _unitdir}
install -D -m 0644 src/sbd.service $RPM_BUILD_ROOT/%{_unitdir}/sbd.service
install -D -m 0644 src/sbd_remote.service $RPM_BUILD_ROOT/%{_unitdir}/sbd_remote.service
%endif

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig
install -m 644 src/sbd.sysconfig ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/sbd

###########################################################

%clean
rm -rf %{buildroot}

%if %{defined _unitdir}
%post
%systemd_post sbd.service
%systemd_post sbd_remote.service
if [ $1 -ne 1 ] ; then
	if systemctl --quiet is-enabled sbd.service 2>/dev/null
	then
		systemctl --quiet reenable sbd.service 2>/dev/null || :
	fi
	if systemctl --quiet is-enabled sbd_remote.service 2>/dev/null
	then
		systemctl --quiet reenable sbd_remote.service 2>/dev/null || :
	fi
fi

%preun
%systemd_preun sbd.service
%systemd_preun sbd_remote.service

%postun
%systemd_postun sbd.service
%systemd_postun sbd_remote.service
%endif

%files
###########################################################
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/sysconfig/sbd
%{_sbindir}/sbd
#%{_datadir}/sbd
%doc %{_mandir}/man8/sbd*
%if %{defined _unitdir}
%{_unitdir}/sbd.service
%{_unitdir}/sbd_remote.service
%endif
%doc COPYING

%changelog
* Tue Jul 10 2018 Mark Syms <mark.syms@citrix.com>  Edwin Török <edvin.torok@citrix.com> - 1.3.1-7.xs+2.0.0
- CA-290600: Xapi SBD watcher segfault
- CA-292257: fix up possible race condition, code refactoring, error improvements
- CA-292257: increase log severity
- Add Xapi health check monitoring
- Use versioned xenserver-corosync Provides
- Depend on our repatched version of packages
- only report good health if quorate or not had quorum
- sbd-cluster: only connect to quorum service if SUPPORT_COROSYNC
- sbd-cluster: disconnect from crm on failure to connect to quorum
- CP-26038: Increase logging level to CRIT for quorum loss

* Mon Jan 15 2018 <kwenning@redhat.com> - 1.3.1-7
- reenable sbd on upgrade so that additional
  links to make pacemaker properly depend on
  sbd are created

  Resolves: rhbz#1525981

* Wed Jan 10 2018 <kwenning@redhat.com> - 1.3.1-5
- add man sections for query- & test-watchdog

  Resolves: rhbz#1462002

* Wed Dec 20 2017 <kwenning@redhat.com> - 1.3.1-3
- mention timeout caveat with SBD_DELAY_START
  in configuration template
- make systemd wait for sbd-start to finish
  before starting pacemaker or dlm

  Resolves: rhbz#1525981

* Fri Nov 3 2017 <kwenning@redhat.com> - 1.3.1-2
- rebase to upstream v1.3.1

  Resolves: rhbz#1499864
            rhbz#1468580
            rhbz#1462002

* Wed Jun 7 2017 <kwenning@redhat.com> - 1.3.0-3
- prevent creation of duplicate servants
- check 2Node flag in corosync to support
  2-node-clusters with shared disk fencing
- move disk-triggered reboot/off/crashdump
  to inquisitor to have sysrq observed by watchdog

  Resolves: rhbz#1413951

* Sun Mar 26 2017 <kwenning@redhat.com> - 1.3.0-1
- rebase to upstream v1.3.0
- remove watchdog-limitation from description
  Resolves: rhbz#1413951

* Mon Feb 27 2017 <kwenning@redhat.com> - 1.2.1-23
- if shared-storage enabled check for node-name <= 63 chars
  Resolves: rhbz#1413951

* Tue Jan 31 2017 <kwenning@redhat.com> - 1.2.1-22
- Rebuild with shared-storage enabled
- Package original manpage
- Added ppc64le target
  Resolves: rhbz#1413951

* Fri Apr 15 2016 <kwenning@redhat.com> - 1.2.1-21
- Rebuild for new pacemaker
  Resolves: rhbz#1320400

* Fri Apr 15 2016 <kwenning@redhat.com> - 1.2.1-20
- tarball updated to c511b0692784a7085df4b1ae35748fb318fa79ee
  from https://github.com/Clusterlabs/sbd
  Resolves: rhbz#1324240

* Thu Jul 23 2015 <abeekhof@redhat.com> - 1.2.1-5
- Rebuild for pacemaker

* Tue Jun 02 2015 <abeekhof@redhat.com> - 1.2.1-4
- Include the dist tag in the release string
- Rebuild for new pacemaker

* Mon Jan 12 2015 <abeekhof@redhat.com> - 1.2.1-3
- Correctly parse SBD_WATCHDOG_TIMEOUT into seconds (not milliseconds)

* Mon Oct 27 2014 <abeekhof@redhat.com> - 1.2.1-2
- Correctly enable /proc/pid validation for sbd_lock_running()

* Fri Oct 24 2014 <abeekhof@redhat.com> - 1.2.1-1
- Further improve integration with the el7 environment

* Thu Oct 16 2014 <abeekhof@redhat.com> - 1.2.1-0.5.872e82f3.git
- Disable unsupported functionality (for now)

* Wed Oct 15 2014 <abeekhof@redhat.com> - 1.2.1-0.4.872e82f3.git
- Improved integration with the el7 environment

* Tue Sep 30 2014 <abeekhof@redhat.com> - 1.2.1-0.3.8f912945.git
- Only build on archs supported by the HA Add-on

* Fri Aug 29 2014 <abeekhof@redhat.com> - 1.2.1-0.2.8f912945.git
- Remove some additional SUSE-isms

* Fri Aug 29 2014 <abeekhof@redhat.com> - 1.2.1-0.1.8f912945.git
- Prepare for package review
  Resolves: rhbz#1134245
