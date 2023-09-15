Name: %{_org}_%{_app}
Requires: httpd
Requires: httpd-devel
Requires: python3
Requires: python3-pip
Requires: python3-mod_wsgi
#Requires: virtualenv
Requires: mod_ssl
Requires: policycoreutils-python-utils

Packager: %{_packager}
Version: %{_version}
Release: %{_release}
Summary: %{_summary}
License: %{_license}
%if "%{_url}" != "--"
URL: %{_url}
%endif
%if "%{_vendor}" != "--"
Vendor: %{_vendor}
%endif
%if "%{_group}" != "--"
Group: %{_group}
%endif
%description
%include %{_description_file}

%changelog
* Tue May 23 2023 George Tsiones <gtsiones@comcast.net> - 0.1-000001
- Created


%prep
rm -rf ./wheels
rm -rf ./venv

mkdir -p ./wheels
python3 -m venv ./venv
source ./venv/bin/activate
python3 -m pip install -U wheel setuptools
python3 "./setup.py" bdist_wheel --dist-dir=./wheels

built_wheel=$(ls ./wheels)

pip download ./wheels/$built_wheel --dest ./wheels

%clean


%install

mkdir -p %{buildroot}/opt/%{_org}/%{_app}
mkdir -p %{buildroot}/etc/httpd/conf.d
mkdir -p %{buildroot}/etc
mkdir -p %{buildroot}/var/www/cgi-bin
mkdir -p %{buildroot}/var/opt/%{_org}/%{_app}
mkdir -p %{buildroot}/etc/profile.d
mkdir -p %{buildroot}/usr
#mkdir -p %{buildroot}/etc/systemd/system/httpd.service.d

cp -a ./config %{buildroot}/opt/%{_org}/%{_app}
cp -a ./config/utah_service_config_fs.pp_txt %{buildroot}/opt/%{_org}/%{_app}/config/utah_service_config.pp_txt
cp -a ./sample_content %{buildroot}/opt/%{_org}/%{_app}
cp -a ./static %{buildroot}/opt/%{_org}/%{_app}
cp -a ./templates %{buildroot}/opt/%{_org}/%{_app}
cp -a ./wheels %{buildroot}/opt/%{_org}/%{_app}
cp ./%{_app}-bootstrap.py %{buildroot}/var/www/cgi-bin
cp -a ./server_config/centos8/etc %{buildroot}


%files 
%config /opt/%{_org}/%{_app}/config
#%attr(0755, root, root) /opt/utah/arches/config
%attr(0755, apache, apache) /opt/%{_org}/%{_app}/sample_content
%attr(0755, apache, apache) /opt/%{_org}/%{_app}/static
%attr(0755, apache, apache) /opt/%{_org}/%{_app}/wheels
%attr(0755, apache, apache) /opt/%{_org}/%{_app}/templates
%attr(0755, apache, apache) /var/www/cgi-bin/%{_app}-bootstrap.py
%attr(0644, apache, apache) /etc/httpd/conf.d/%{_app}-python-wsgi.conf
%attr(0755, apache, apache) /etc/pki/tls/certs/localhost.crt
%attr(0755, apache, apache) /etc/pki/tls/private/localhost.key
%attr(0755, apache, apache) /etc/profile.d/%{_org}_%{_app}_profile.sh
%attr(0755, apache, apache) /var/opt/%{_org}/%{_app}

%post
python3 -m venv /opt/%{_org}/%{_app}/venv
. /opt/%{_org}/%{_app}/venv/bin/activate
pip install --no-index --find-links=/opt/%{_org}/%{_app}/wheels /opt/%{_org}/%{_app}/wheels/*
chown -R apache:apache /opt/%{_org}/%{_app}/venv


if [ -d /var/opt/%{_org}/%{_app}/data ]; then
        echo "Data directory was found will not generate startup data"
else
        su -s /bin/bash - apache -c 'set ARCHES_SVC_LOAD_NAVIGATION=false;$(cd /opt/%{_org}/%{_app}; . ./venv/bin/activate; python3 -m utah.impl.zion.setup); exit'
fi

ln -s /opt/%{_org}/%{_app}/templates /var/www/cgi-bin/templates
ln -s /opt/%{_org}/%{_app}/static /var/www/html/%{_app}-static


# If se linux is enabled and running anything but disabled
if which getenforce > /dev/null 2>&1; then
        if [[ $(getenforce) != "Disabled" ]]; then
                # Configure writable directories so apache cgi can read/write
                semanage fcontext -a -t httpd_sys_rw_content_t '/var/opt/%{_org}/%{_app}(/.*)?'
                restorecon -Rv '/var/opt/%{_org}/%{_app}'
        fi
fi

sed -i -E 's/LANG=C/LANG=C\nEnvironment=UTAH_APP_HOME=\/opt\/%{_org}\/%{_app}\nEnvironment=UTAH_VARIABLE_DATA=\/var\/opt\/%{_org}\/%{_app}/g' /usr/lib/systemd/system/httpd.service

if systemctl > /dev/null 2>&1; then 
        systemctl daemon-reload
fi


%preun
rm -rf /var/www/cgi-bin/templates
rm -rf /var/www/html/arches-static
rm -rf /opt/%{_org}/%{_app}/venv

%postun
rm -rf /opt/%{_org}/%{_app}
if [[ -z "$(ls /opt/%{_org})" ]]; then
        rm -rf /opt/%{_org}
fi