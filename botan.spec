#
# Conditional build:
%bcond_without	tests		# unit tests
%bcond_without	apidocs		# Sphinx based HTML documentation
%bcond_without	static_libs	# static library
%bcond_without	python		# Python bindings
%bcond_without	python2		# CPython 2.x binding
%bcond_without	python3		# CPython 3.x binding

%if %{without python}
%undefine	with_python2
%undefine	with_python3
%endif
Summary:	Crypto library written in C++
Summary(pl.UTF-8):	Biblioteka kryptograficzna napisana w C++
Name:		botan
Version:	1.10.17
Release:	1
License:	BSD
Group:		Libraries
Source0:	https://botan.randombit.net/releases/Botan-%{version}.tgz
# Source0-md5:	e5ed5dc70edd238c5a2116670b2cb3f3
Patch0:		%{name}-includes.patch
Patch1:		%{name}-python.patch
URL:		https://botan.randombit.net/
BuildRequires:	bzip2-devel
BuildRequires:	gmp-devel
BuildRequires:	libstdc++-devel
BuildRequires:	openssl-devel
BuildRequires:	python >= 1:2.6
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
%{?with_apidocs:BuildRequires:	sphinx-pdg}
BuildRequires:	zlib-devel
%if %{with python2}
BuildRequires:	boost-python-devel
BuildRequires:	python-devel >= 1:2.6
%endif
%if %{with python3}
BuildRequires:	boost-python3-devel
BuildRequires:	python3-devel >= 1:3.2
%endif
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
Summary:	Header files for Botan library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki Botan
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	bzip2-devel
Requires:	gmp-devel
Requires:	openssl-devel
Requires:	zlib-devel

%description devel
This package contains the header files for developing applications
that use Botan.

%description devel
Ten pakiet zawiera pliki nagłówkowe do tworzenia aplikacji
wykorzystujących bibliotekę Botan.

%package static
Summary:	Static Botan library
Summary(pl.UTF-8):	Statyczna biblioteka Botan
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static Botan library.

%description static -l pl.UTF-8
Statyczna biblioteka Botan.

%package apidocs
Summary:	Botan API documentation
Summary(pl.UTF-8):	Dokumentacja API biblioteki Botan
Group:		Documentation
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description apidocs
API and internal documentation for Botan library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki Botan.

%package -n python-botan
Summary:	Python 2.x binding for Botan library
Summary(pl.UTF-8):	Wiązanie Pythona 2.x do biblioteki Botan
Group:		Libraries/Python
Requires:	%{name} = %{version}-%{release}

%description -n python-botan
Python 2.x binding for Botan library.

%description -n python-botan -l pl.UTF-8
Wiązanie Pythona 2.x do biblioteki Botan.

%package -n python3-botan
Summary:	Python 3.x binding for Botan library
Summary(pl.UTF-8):	Wiązanie Pythona 3.x do biblioteki Botan
Group:		Libraries/Python
Requires:	%{name} = %{version}-%{release}

%description -n python3-botan
Python 3.x binding for Botan library.

%description -n python3-botan -l pl.UTF-8
Wiązanie Pythona 3.x do biblioteki Botan.

%prep
%setup -q -n Botan-%{version}
%patch0 -p1
%patch1 -p1

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
	--disable-modules=%{disable_modules} \
%if %{with python}
	--with-boost-python \
	--with-python-version=x.y \
%endif
	%{?with_apidocs:--with-sphinx}

# (ab)using CXX as an easy way to inject our CXXFLAGS
%{__make} \
	CXX="%{__cxx} %{rpmcxxflags}"

%if %{with apidocs}
%{__make} docs
%endif

%if %{with tests}
%{__make} check \
	CXX="%{__cxx} %{rpmcxxflags}"

LD_LIBRARY_PATH=. ./check --validate
%endif

%if %{with python2}
install -d build/python%{py_ver}
%{__make} -f Makefile.python \
	CXX="%{__cxx}" \
	CFLAGS="%{rpmcxxflags}" \
	LDFLAGS="%{rpmldflags}" \
	PY_VER=%{py_ver} \
	PYTHON_ROOT=%{py_libdir}/config \
	PYTHON_INC=-I%{py_incdir}
%endif

%if %{with python3}
install -d build/python%{py3_ver}
%{__make} -f Makefile.python \
	CXX="%{__cxx}" \
	CFLAGS="%{rpmcxxflags}" \
	LDFLAGS="%{rpmldflags}" \
	BOOST_PYTHON=boost_python3 \
	PY_VER=%{py3_ver} \
	PYTHON_ROOT=%{py3_libdir}/config \
	PYTHON_INC=-I%{py3_incdir}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	INSTALL_CMD_EXEC="install -p -m 755" \
	INSTALL_CMD_DATA="install -p -m 644" \
	DOCDIR=_doc \
	DESTDIR=$RPM_BUILD_ROOT%{_prefix}

%if %{with python2}
%{__make} -f Makefile.python install \
	PY_VER=%{py_ver} \
	PYTHON_SITE_PACKAGE_DIR=$RPM_BUILD_ROOT%{py_sitedir}

%py_comp $RPM_BUILD_ROOT%{py_sitedir}
%py_ocomp $RPM_BUILD_ROOT%{py_sitedir}
%py_postclean
%endif

%if %{with python3}
%{__make} -f Makefile.python install \
	PY_VER=%{py3_ver} \
	PYTHON_SITE_PACKAGE_DIR=$RPM_BUILD_ROOT%{py3_sitedir}

%py3_comp $RPM_BUILD_ROOT%{py3_sitedir}
%py3_ocomp $RPM_BUILD_ROOT%{py3_sitedir}
%endif

%if %{with apidocs}
install -d $RPM_BUILD_ROOT%{_examplesdir}
cp -pr doc/examples $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc readme.txt doc/{algos,credits,faq,index,license,log,support,users}.txt
%attr(755,root,root) %{_libdir}/libbotan-1.10.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libbotan-1.10.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/botan-config-1.10
%attr(755,root,root) %{_libdir}/libbotan-1.10.so
%{_includedir}/botan-1.10
%{_pkgconfigdir}/botan-1.10.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libbotan-1.10.a
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc _doc/manual/{_static,*.html,*.js}
%{_examplesdir}/%{name}-%{version}
%endif

%if %{with python2}
%files -n python-botan
%defattr(644,root,root,755)
%dir %{py_sitedir}/botan
%attr(755,root,root) %{py_sitedir}/botan/_botan.so
%{py_sitedir}/botan/__init__.py[co]
%endif

%if %{with python3}
%files -n python3-botan
%defattr(644,root,root,755)
%dir %{py3_sitedir}/botan
%attr(755,root,root) %{py3_sitedir}/botan/_botan.so
%{py3_sitedir}/botan/__init__.py
%{py3_sitedir}/botan/__pycache__
%endif
