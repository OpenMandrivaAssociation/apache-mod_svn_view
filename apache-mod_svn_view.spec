#Module-Specific definitions
%define mod_name mod_svn_view
%define mod_conf A59_%{mod_name}.conf
%define mod_so %{mod_name}.so

%define snap r147

Summary:	Mod_svn_view provides a web-based view of a Subversion repository
Name:		apache-%{mod_name}
Version:	0.1.0
Release:	%mkrel 1.%{snap}.6
Group:		System/Servers
License:	GPL
URL:		http://www.outoforder.cc/projects/apache/mod_svn_view/
Source0:	%{mod_name}-%{version}-%{snap}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		mod_svn_view-autofoofix.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.0.54
Requires(pre):	apache >= 2.0.54
Requires:	apache-conf >= 2.0.54
Requires:	apache >= 2.0.54
Requires:	apache-mod_transform
BuildRequires:  apache-devel >= 2.0.54
BuildRequires:	autoconf2.5
BuildRequires:	automake1.8
BuildRequires:	subversion-devel
BuildRequires:	libtool
BuildRequires:	libxml2-devel >= 2.6.11
BuildRequires:	libxslt-devel >= 1.1.5
BuildRequires:	file
BuildRequires:	python
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_svn_view provides a web-based view of a Subversion repository, similar to
Chora, or viewcvs. What makes mod_svn_view different is it uses the Subversion
libraries directly instead of executing the command line client, and thus has
tremendous speed. It is also written in C as an Apache 2.0 module and generates
a simple XML output that can be run through XSL Transformations via
mod_transform to generate a customized look. 

%prep

%setup -q -n %{mod_name}
#%patch0 -p0

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type d -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# libtool
perl -pi -e "s|AC_PROG_RANLIB|AC_PROG_LIBTOOL|g" configure*

# fix apr
if [ -x %{_bindir}/apr-config ]; then APR=%{_bindir}/apr-config; fi || echo APR=%{_bindir}/apr-1-config
if [ -x %{_bindir}/apu-config ]; then APU=%{_bindir}/apu-config; fi || echo APU=%{_bindir}/apu-1-config
perl -pi -e "s|%{_bindir}/apr-config|$APR|g" m4/*.m4
perl -pi -e "s|%{_bindir}/apu-config|$APU|g" m4/*.m4

# lib64 fix
perl -pi -e "s|/lib\b|/%{_lib}|g" m4/*.m4

%build
rm -rf autom4te.cache
touch ./config.in
#libtoolize --force --copy; aclocal-1.7 -I m4; automake-1.7 --add-missing --copy --foreign; autoheader; autoconf

if [ -x %{_bindir}/apr-config ]; then APR=%{_bindir}/apr-config; fi || echo APR=%{_bindir}/apr-1-config
if [ -x %{_bindir}/apu-config ]; then APU=%{_bindir}/apu-config; fi || echo APU=%{_bindir}/apu-1-config

export CFLAGS="`%{_sbindir}/apxs -q CFLAGS` `$APR --cflags --includes`"
export CXXFLAGS="`%{_sbindir}/apxs -q CFLAGS` `$APR --cflags --includes`"
#export LIBTOOL="`$APR --apr-libtool`"

sh ./autogen.sh
autoconf

%configure2_5x --localstatedir=/var/lib

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -d %{buildroot}/var/www/mod_svn_view/xslt
install -d %{buildroot}/var/www/mod_svn_view/themes/blueview

install -m0644 themes/blueview/* %{buildroot}/var/www/mod_svn_view/themes/blueview
install -m0644 xslt/default.xsl %{buildroot}/var/www/mod_svn_view/xslt/default.xsl

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}/var/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}/var/www/html/addon-modules/%{name}-%{version}

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CREDITS LICENSE NOTICE
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0644,root,root) %config(noreplace) /var/www/mod_svn_view/xslt/default.xsl
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
/var/www/html/addon-modules/*
/var/www/mod_svn_view/themes/blueview


