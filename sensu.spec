
%global gem_name sensu

Name:           %{gem_name}
Version:        0.27.0.beta.2
Release:        2%{?dist}
Summary:        A monitoring framework
Group:          Development/Languages
License:        MIT
URL:            https://github.com/sensu/sensu
Source0:        https://rubygems.org/downloads/%{gem_name}-%{version}.gem
Source1:        https://github.com/sensu/sensu/archive/v%{version}.tar.gz#/%{gem_name}-%{version}.tar.gz
Source2:        sensu-api.service
Source3:        sensu-client.service
Source4:        sensu-server.service
Source5:        sensu.sysconfig
Source6:        sensu.logrotate
Source7:        sensu.config
Patch1:         0001-Disable-network-based-tests.patch

BuildRequires:      ruby
BuildRequires:      rubygems-devel
BuildRequires:      systemd
# test suite requirements
BuildRequires:      rubygem(rspec)
BuildRequires:      rubygem(addressable)
BuildRequires:      rubygem(em-http-request) >= 1.1.5
# test suite runtime requirements
BuildRequires:      rubygem(em-http-server) >= 0.1.8
BuildRequires:      rubygem(eventmachine) >= 1.2.1
BuildRequires:      rubygem(sensu-extension) >= 1.5.1
BuildRequires:      rubygem(sensu-extensions) >= 1.7.1
BuildRequires:      rubygem(sensu-json) >= 2.0.1
BuildRequires:      rubygem(sensu-logger) >= 1.2.1
BuildRequires:      rubygem(sensu-redis) >= 2.1.0
BuildRequires:      rubygem(sensu-settings) >= 9.6.0
BuildRequires:      rubygem(sensu-spawn) >= 2.2.1
BuildRequires:      rubygem(sensu-transport) >= 7.0.2

Requires(pre):      shadow-utils
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
# runtime requirements
Requires:           rubygem(em-http-server) >= 0.1.8
Requires:           rubygem(eventmachine) >= 1.2.1
Requires:           rubygem(sensu-extension) >= 1.5.1
Requires:           rubygem(sensu-extensions) >= 1.7.1
Requires:           rubygem(sensu-json) >= 2.0.1
Requires:           rubygem(sensu-logger) >= 1.2.1
Requires:           rubygem(sensu-redis) >= 2.1.0
Requires:           rubygem(sensu-settings) >= 9.6.0
Requires:           rubygem(sensu-spawn) >= 2.2.1
Requires:           rubygem(sensu-transport) >= 7.0.2

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
# relax generated dependencies
sed -i 's#s.add_\(.*\)dependency(\(.*\), \["= \(.*\)"\])#s.add_\1dependency(\2, \["~> \3"\]\)#' %{gem_name}.gemspec
# prepare unit test suite
tar -xzf %{SOURCE1}
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

# install systemd service files
mkdir -p %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/
install -p -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/
install -p -m 0644 %{SOURCE4} %{buildroot}%{_unitdir}/
# install sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
# install logrotate
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
install -p -m 0644 %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
# install default config
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/conf.d
install -p -m 0644 %{SOURCE7} %{buildroot}%{_sysconfdir}/%{name}/config.json
# install remaining directory structure and files
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
touch %{buildroot}%{_localstatedir}/log/%{name}/%{name}-client.log
touch %{buildroot}%{_localstatedir}/log/%{name}/%{name}-server.log
touch %{buildroot}%{_localstatedir}/log/%{name}/%{name}-api.log
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

%check
pushd .%{gem_instdir}
# TO-DO: Most of the tests are disabled (by Patch1) due to network connection
#        requirement. This should be mocked / fixed in the future
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
%attr(0770, sensu, sensu) %{_localstatedir}/log/%{name}/%{name}-client.log
%attr(0770, sensu, sensu) %{_localstatedir}/log/%{name}/%{name}-server.log
%attr(0770, sensu, sensu) %{_localstatedir}/log/%{name}/%{name}-api.log
%attr(0770, sensu, sensu) %{_sharedstatedir}/%{name}
%exclude %{gem_cache}
%{gem_spec}

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/CHANGELOG.md
%doc %{gem_instdir}/MIT-LICENSE.txt
%doc %{gem_instdir}/README.md
%doc %{gem_instdir}/%{gem_name}.gemspec
%{gem_instdir}/spec

%changelog
* Wed Jan 04 2017 Martin Mágr <mmagr@redhat.com> - 0.27.0.beta.2-2
- Add configuration install back

* Mon Jan 02 2017 Martin Mágr <mmagr@redhat.com> - 0.27.0.beta.2-1
- Updated to latest upstream version
- Fixed log files permissions
- Use own systemd service files, logrotate config and sysconfig

* Fri Aug 12 2016 Martin Mágr <mmagr@redhat.com> - 0.23.2-3
- Relax dependencies so the package works with EPEL packages

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
