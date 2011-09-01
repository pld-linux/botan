#
# Conditional build:
%bcond_without	tests		# build without tests
%bcond_without	apidocs		# do not build and package API docs
%bcond_without	static_libs	# don't build static libraries

Summary:	Crypto library written in C++
Name:		botan
Version:	1.8.13
Release:	1
License:	BSD
Group:		Libraries
URL:		http://botan.randombit.net/
# tarfile is stripped using repack.sh. original tarfile to be found
# here: http://files.randombit.net/botan/Botan-%%{version}.tbz
Source0:	http://pkgs.fedoraproject.org/repo/pkgs/botan/Botan-%{version}.stripped.tbz/e1cf4c2990a60867603fc111f0715e24/Botan-%{version}.stripped.tbz
# Source0-md5:	e1cf4c2990a60867603fc111f0715e24
Source1:	README.fedora
# soname was changed unintentionally upstream, revert it.
Patch0:		soname.patch
BuildRequires:	bzip2-devel
BuildRequires:	gmp-devel
BuildRequires:	libstdc++-devel
BuildRequires:	openssl-devel
BuildRequires:	python
BuildRequires:	zlib-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Botan is a BSD-licensed crypto library written in C++. It provides a
wide variety of basic cryptographic algorithms, X.509 certificates and
CRLs, PKCS \#10 certificate requests, a filter/pipe message processing
system, and a wide variety of other features, all written in portable
C++. The API reference, tutorial, and examples may help impart the
flavor of the library.

%package devel
Summary:	Development files for botan
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	bzip2-devel
Requires:	gmp-devel
Requires:	openssl-devel
Requires:	pkgconfig
Requires:	zlib-devel

%description devel
This package contains libraries and header files for developing
applications that use botan.

%package static
Summary:	Static botan library
Summary(pl.UTF-8):	Statyczna biblioteka botan
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static botan library.

%description static -l pl.UTF-8
Statyczna biblioteka botan.

%package apidocs
Summary:	botan API documentation
Summary(pl.UTF-8):	Dokumentacja API biblioteki botan
Group:		Documentation

%description apidocs
API and internal documentation for botan library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki botan.

%prep
%setup -q -n Botan-%{version}
%patch0 -p0
cp -p %{SOURCE1} .

%build
# we have the necessary prerequisites, so enable optional modules
%define enable_modules gnump,bzip2,zlib,openssl

# fixme: maybe disable unix_procs, very slow.
%define disable_modules %{nil}

./configure.py \
	--prefix=%{_prefix} \
	--libdir=%{_lib} \
	--cc=gcc \
	--os=linux \
	--cpu=%{_arch} \
	--enable-modules=%{enable_modules} \
	--disable-modules=%{disable_modules}

# (ab)using CXX as an easy way to inject our CXXFLAGS
%{__make} \
	CXX="%{__cxx} %{rpmcxxflags}"

%if %{with tests}
%{__make} \
	CXX="%{__cxx} %{rpmcxxflags}" check

# these checks would fail
mv checks/validate.dat{,.orig}
awk '/\[.*\]/{f=0} /\[(RC5.*|RC6|IDEA)\]/{f=1} (f && !/^#/){sub(/^/,"#")} {print}' \
	checks/validate.dat.orig > checks/validate.dat
LD_LIBRARY_PATH=. ./check --validate
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	INSTALL_CMD_EXEC="install -p -m 755" \
	INSTALL_CMD_DATA="install -p -m 644" \
	DOCDIR=_doc \
	DESTDIR=$RPM_BUILD_ROOT%{_prefix}

%clean
rm -rf $RPM_BUILD_ROOT

# not packaging shared lib properly, so no ldconfig needed
#%post	-p /sbin/ldconfig
#%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc _doc/readme.txt _doc/log.txt _doc/thanks.txt _doc/credits.txt
%doc _doc/license.txt _doc/fips140.tex _doc/pgpkeys.asc
%doc README.fedora
%attr(755,root,root) %{_libdir}/libbotan-1.8.*.so

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/botan-config
%{_includedir}/botan
%{_libdir}/libbotan.so
%{_pkgconfigdir}/botan-1.8.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libbotan.a
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc doc/examples
%doc _doc/api* _doc/tutorial*
%endif
