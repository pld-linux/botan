#
# Conditional build:
%bcond_without	tests		# build without tests
%bcond_without	apidocs		# do not build and package API docs
%bcond_without	static_libs	# don't build static libraries

Summary:	Crypto library written in C++
Summary(pl.UTF-8):	Biblioteka kryptograficzna napisana w C++
Name:		botan
Version:	1.8.14
Release:	3
License:	BSD
Group:		Libraries
# tarfile is stripped using repack.sh. original tarfile to be found
# here: http://files.randombit.net/botan/Botan-%%{version}.tbz
Source0:	http://pkgs.fedoraproject.org/repo/pkgs/botan/Botan-%{version}.stripped.tbz/4b5ce78b1cfc0735eb7ec4f6903068ca/Botan-%{version}.stripped.tbz
# Source0-md5:	4b5ce78b1cfc0735eb7ec4f6903068ca
Source1:	README.fedora
# soname was changed unintentionally upstream, revert it.
Patch0:		soname.patch
URL:		http://botan.randombit.net/
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
CRLs, PKCS#10 certificate requests, a filter/pipe message processing
system, and a wide variety of other features, all written in portable
C++. The API reference, tutorial, and examples may help impart the
flavor of the library.

%description -l pl.UTF-8
Botan to biblioteka kryptograficzna na licencji BSD, napisana w C++.
Zapewnia szeroki zakres algorytmów kryptograficznych, certyfikaty
X.509 oraz CRL, żądania certyfikatów PKCS#10, system przetwarzania
komunikatów z filtrowaniem/potokami i wiele innych funkcji, wszystko
napisane w przenośnym C++. Dodatkowe udogodnienia to dokumentacja API,
wprowadzenie oraz przykłady.

%package devel
Summary:	Header files for botan library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki botan
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	bzip2-devel
Requires:	gmp-devel
Requires:	openssl-devel
Requires:	zlib-devel

%description devel
This package contains the header files for developing applications
that use botan.

%description devel
Ten pakiet zawiera pliki nagłówkowe do tworzenia aplikacji
wykorzystujących bibliotekę botan.

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
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

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
%{__mv} checks/validate.dat{,.orig}
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

rm $RPM_BUILD_ROOT%{_bindir}/botan-config

%clean
rm -rf $RPM_BUILD_ROOT

# NOTE: only update ld.so cache, there are no symlinks
%post	-p /sbin/postshell
/sbin/ldconfig -X
%postun	-p /sbin/postshell
/sbin/ldconfig -X

%files
%defattr(644,root,root,755)
%doc _doc/{credits,license,log,readme,thanks}.txt _doc/{fips140.tex,pgpkeys.asc} README.fedora
%attr(755,root,root) %{_libdir}/libbotan-1.8.*.so

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libbotan.so
%{_includedir}/botan
%{_pkgconfigdir}/botan-1.8.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libbotan.a
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc doc/examples _doc/{api*,tutorial*}
%endif
