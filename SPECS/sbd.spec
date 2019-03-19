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
%global commit 4968e9c8602fbb990bed63cc96ca18f62e2181db
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global github_owner Clusterlabs
%global buildnum 4

Name:           sbd
Summary:        Storage-based death
License:        GPLv2+
Group:          System Environment/Daemons
Version:        1.3.0
Release:        6.xs+1.0.0
Url:            https://github.com/%{github_owner}/%{name}
#Source0:        https://github.com/%{github_owner}/%{name}/archive/%{commit}/%{name}-%{commit}.tar.gz
Source0:         https://code.citrite.net/rest/archive/latest/projects/XSU/repos/%{name}/archive?at=%{commit}&format=tar.gz&prefix=%{name}-%{commit}#/%{name}-%{commit}.tar.gz
Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XS/repos/sbd.pg/archive?at=1.0.0&format=tar) = 0697b802cd174778a2693ccee415a014c5f67c7e
Patch0:         01-Fix-sbd-inquisitor-Correctly-look-up-servant-by-devi.patch
Patch1:         02-Fix-sbd-inquisitor-Do-not-create-duplicate-servants.patch
Patch2:         03-Fix-cluster-servant-check-for-corosync-2Node-mode.patch
Patch3:         04-Refactor-servant-type-helpers.patch
Patch4:         05-Fix-disk-servant-signal-reset-request-via-exit-code.patch
Patch5: 0001-sbd-cluster-only-report-good-health-if-quorate-or-no.patch
Patch6: 0002-increase_logging_level_to_CRIT_for_quorum_loss.patch
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
* Thu Mar 15 2018 Edwin Török <edvin.torok@citrix.com> - 1.3.0-6.xs+1.0.0
- Use versioned xenserver-corosync Provides
- Depend on our repatched version of packages

* Fri Feb 16 2018 Mark Syms <mark.syms@citrix.com> - 1.3.0-5.xs-1.0.0
- only report good health if quorate or not had quorum
- sbd-cluster: only connect to quorum service if SUPPORT_COROSYNC
- sbd-cluster: disconnect from crm on failure to connect to quorum
- CP-26038: Increase logging level to CRIT for quorum loss

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
