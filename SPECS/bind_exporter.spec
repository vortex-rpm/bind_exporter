%define debug_package %{nil}

%define _git git20170119

Name:    bind_exporter
Version: 0.0
Release: 0.%{_git}%{?dist}
Summary: Prometheus exporter for BIND
License: ASL 2.0
Vendor:  Vortex RPM
URL:     https://github.com/digitalocean/bind_exporter

Source0: %{name}-%{_git}.tar.gz
Source1: %{name}.service
Source2: %{name}.default
Source3: %{name}.init

%{?el6:Requires(post): chkconfig}
%{?el6:Requires(preun): chkconfig, initscripts}
%{?el7:%{?systemd_requires}}
Requires(pre): shadow-utils
BuildRequires: golang, git

%description

Export BIND(named/dns) v9+ service metrics to Prometheus.

%prep

%setup -q -n %{name}-%{_git}

%build
mkdir _build
export GOPATH=$(pwd)/_build
go get -v -d
go build -v %{name}.go

%install
mkdir -vp %{buildroot}/var/lib/prometheus
mkdir -vp %{buildroot}/usr/bin
%{?el6:mkdir -vp %{buildroot}%{initddir}}
%{?el7:mkdir -vp %{buildroot}/usr/lib/systemd/system}
mkdir -vp %{buildroot}/etc/default
install -m 755 %{name} %{buildroot}/usr/bin/%{name}
%{?el6:install -m 755 %{name}.init %{buildroot}%{_initddir}/%{name}}
%{?el7:install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/%{name}.service}
install -m 644 %{SOURCE2} %{buildroot}/etc/default/%{name}

%pre
getent group prometheus >/dev/null || groupadd -r prometheus
getent passwd prometheus >/dev/null || \
  useradd -r -g prometheus -d /var/lib/prometheus -s /sbin/nologin \
          -c "Prometheus services" prometheus
exit 0

%post
%{?el6:/sbin/chkconfig --add %{name}}
%{?el7:%systemd_post %{name}.service}

%preun
%{?el6:
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
}
%{?el7:%systemd_preun %{name}.service}

%postun
i%{?el6
:f [ "$1" -ge "1" ] ; then
    /sbin/service %{name} restart >/dev/null 2>&1
fi
}
%{?el7:%systemd_postun %{name}.service}

%files
%defattr(-,root,root,-)
/usr/bin/%{name}
%{?el7:/usr/lib/systemd/system/%{name}.service}
%{?el6:%{_initddir}/%{name}}
%config(noreplace) /etc/default/%{name}
%attr(755, prometheus, prometheus)/var/lib/prometheus
%doc CHANGELOG.md LICENSE NOTICE README.md

%changelog
* Thu Jan 19 2017 Ilya Otyutskiy <ilya.otyutskiy@icloud.com> - 0.0-0.git20170119.vortex
- Initial packaging
