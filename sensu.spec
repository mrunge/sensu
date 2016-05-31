# Generated from sensu-0.16.0.gem by gem2rpm -*- rpm-spec -*-
%global gem_name sensu
%global sensu_build_release 2

Name:           %{gem_name}
Version:        0.23.2
Release:        2%{?dist}
Summary:        A monitoring framework
Group:          Development/Languages
License:        MIT
URL:            https://github.com/sensu/sensu
Source0:        https://rubygems.org/gems/%{gem_name}-%{version}.gem
Source1:        https://github.com/sensu/sensu-build/archive/%{version}-%{sensu_build_release}.tar.gz
Source2:        https://github.com/sensu/sensu/archive/v%{version}.tar.gz
Patch0:         sensu-sensu-build-fix-systemd-unit-binary-paths.patch
Patch1:         0001-Disable-network-based-tests.patch

BuildRequires:      ruby
BuildRequires:      rubygems-devel
BuildRequires:      systemd
BuildRequires:      rubygem(rspec)
BuildRequires:      rubygem(addressable)

BuildRequires:      rubygem(async_sinatra) >= 1.2.0
BuildRequires:      rubygem(eventmachine) = 1.2.0.1
BuildRequires:      rubygem(sensu-extension) = 1.5.0
BuildRequires:      rubygem(sensu-extensions) = 1.5.0
BuildRequires:      rubygem(sensu-json) = 1.1.1
BuildRequires:      rubygem(sensu-logger) = 1.2.0
BuildRequires:      rubygem(sensu-redis) = 1.3.0
BuildRequires:      rubygem(sensu-settings) = 3.4.0
BuildRequires:      rubygem(sensu-spawn) = 1.8.0
BuildRequires:      rubygem(sensu-transport) = 5.0.0
BuildRequires:      rubygem(sinatra) >= 1.4.6
BuildRequires:      rubygem(thin) >= 1.6.3

Requires(pre):      shadow-utils
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
Requires:           rubygem(async_sinatra) >= 1.2.0
Requires:           rubygem(eventmachine) = 1.2.0.1
Requires:           rubygem(sensu-extension) = 1.5.0
Requires:           rubygem(sensu-extensions) = 1.5.0
Requires:           rubygem(sensu-json) = 1.1.1
Requires:           rubygem(sensu-logger) = 1.2.0
Requires:           rubygem(sensu-redis) = 1.3.0
Requires:           rubygem(sensu-settings) = 3.4.0
Requires:           rubygem(sensu-spawn) = 1.8.0
Requires:           rubygem(sensu-transport) = 5.0.0
Requires:           rubygem(sinatra) >= 1.4.6
Requires:           rubygem(thin) >= 1.6.3

BuildArch: noarch

%description
A monitoring framework that aims to be simple, malleable, and scalable.


%package doc
Summary:        Documentation for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description doc
Documentation for %{name}.

%prep
gem unpack %{SOURCE0}
%setup -q -D -T -n  %{gem_name}-%{version}
gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec

tar -xzf %{SOURCE1}
pushd sensu-build-%{version}-%{sensu_build_release}
%patch0
popd

tar -xzf %{SOURCE2}
pushd ./%{gem_name}-%{version}
%patch1 -p1
popd

%build
# Create the gem as gem install only works on a gem file
gem build %{gem_name}.gemspec

# %%gem_install compiles any C extensions and installs the gem into ./%%gem_dir
# by default, so that we can move it into the buildroot in %%install
%gem_install
# Copy unit tests
mv %{_builddir}/%{gem_name}-%{version}/%{gem_name}-%{version}/spec .%{gem_instdir}

%install
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/


mkdir -p %{buildroot}%{_bindir}
cp -pa .%{_bindir}/* \
        %{buildroot}%{_bindir}/

find %{buildroot}%{gem_instdir}/exe -type f | xargs chmod a+x

mkdir -p %{buildroot}%{_unitdir}
rm -f sensu-build-%{version}-%{sensu_build_release}/sensu_configs/systemd/sensu-runsvdir.service
install -p -m 0644 sensu-build-%{version}-%{sensu_build_release}/sensu_configs/systemd/*.service %{buildroot}%{_unitdir}/

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 0644 sensu-build-%{version}-%{sensu_build_release}/sensu_configs/default/%{name} %{buildroot}%{_sysconfdir}/sysconfig

mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
install -p -m 0644 sensu-build-%{version}-%{sensu_build_release}/sensu_configs/logrotate.d/%{name} %{buildroot}%{_sysconfdir}/logrotate.d

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -ar sensu-build-%{version}-%{sensu_build_release}/sensu_configs/%{name}/* %{buildroot}%{_sysconfdir}/%{name}

mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

%check
pushd .%{gem_instdir}
# TO-DO: Most of the tests are disabled (by Patch1) due to network connection
#        requirement and dependency on em-http-request which is tricky to package.
#        This should be mocked / fixed in the future
rspec spec
popd

%pre
getent group sensu >/dev/null || groupadd -r sensu
getent passwd sensu >/dev/null || \
    useradd -r -g sensu -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
    -c "Sensu monitoring software" sensu
exit 0

%post
%systemd_post sensu-server.service sensu-client.service sensu-api.service

%preun
%systemd_preun sensu-server.service sensu-client.service sensu-api.service

%postun
%systemd_postun sensu-server.service sensu-client.service sensu-api.service

%files
%dir %{gem_instdir}
%{_bindir}/sensu-server
%{_bindir}/sensu-client
%{_bindir}/sensu-api
%{_bindir}/sensu-install
%{gem_instdir}/exe
%{gem_libdir}
%{_unitdir}/*.service
%{_sysconfdir}/sysconfig/%{name}
%{_sysconfdir}/logrotate.d/%{name}
%attr(0770, sensu, sensu) %{_sysconfdir}/%{name}
%attr(0770, sensu, sensu) %{_localstatedir}/log/%{name}
%attr(0770, sensu, sensu) %{_sharedstatedir}/%{name}
%exclude %{gem_cache}
%{gem_spec}
%doc %{gem_instdir}/CHANGELOG.md
%doc %{gem_instdir}/MIT-LICENSE.txt
%doc %{gem_instdir}/README.md

%files doc
%doc %{gem_docdir}
%{gem_instdir}/%{gem_name}.gemspec
%{gem_instdir}/spec

%changelog
* Tue May 31 2016 Martin Mágr <mmagr@redhat.com> - 0.23.2-2
- Changed home directory for user sensu to /var/lib/sensu

* Mon May 09 2016 Martin Mágr <mmagr@redhat.com> - 0.23.2-1
- Updated to upstream version 0.23.2
- Run at least some of the unit tests

* Mon Mar 07 2016 Martin Mágr <mmagr@redhat.com> - 0.22.0-1
- Updated to upstream version 0.22.0

* Thu Jun 18 2015 Graeme Gillies <ggillies@redhat.com> - 0.16.0-2
- Corrected spec file macro so explicit dependencies for EL7 are included

* Fri Jan 23 2015 Graeme Gillies <ggillies@redhat.com> - 0.16.0-1
- Initial package
