Name:		clisp
Summary:	Common Lisp (ANSI CL) implementation
Version:	2.34
Release: 	2%{?dist}

Group:		Development/Languages
License:	GPL
URL:		http://sourceforge.net/projects/clisp
Source:		http://download.sourceforge.net/clisp/clisp-2.34.tar.bz2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	readline-devel, XFree86-devel, gettext, pcre-devel, postgresql-devel
BuildRequires:	libsigsegv-devel, db4-devel, zlib-devel


%description
Common Lisp is a high-level, general-purpose programming language.
GNU CLISP is a Common Lisp implementation by Bruno Haible of Karlsruhe
University and Michael Stoll of Munich University, both in Germany.
It mostly supports the Lisp described in the ANSI Common Lisp
standard.

GNU CLISP includes an interpreter, a compiler, a debugger, a large
subset of CLOS, a foreign language interface and a socket interface.
An X11 interface is available through CLX, Garnet, CLUE/CLIO.  GNU
CLISP runs Maxima, ACL2 and many other Common Lisp packages.


%package devel
Summary:	Development files for CLISP
Group:		Development/Languages
Requires:	%{name} = %{version}-%{release}

%description devel
Files necessary for linking CLISP.

%prep
%setup -q


%build
sed -i -e 's|-Wpointer-arith|-Wpointer-arith -falign-functions=4|' src/makemake.in
# during test phase something goes wrong during file copying, so disable check
sed -i -e 's|^  make check$||' configure
# setting CFLAGS breaks the build
./configure --prefix=%{_prefix} \
	    --libdir=%{_libdir} \
	    --fsstnd=redhat \
	    --with-dynamic-ffi \
	    --with-module=berkeley-db \
	    --with-module=clx/new-clx \
	    --with-module=i18n \
	    --with-module=pcre \
	    --with-module=postgresql \
	    --with-module=rawsock \
	    --with-module=regexp \
	    --with-module=syscalls \
	    --with-module=wildcard \
	    --with-module=zlib \
   	    --with-module=bindings/glibc \
	    --with-readline \
	    --build


%install
rm -rf $RPM_BUILD_ROOT
make -C src prefix=%{_prefix} libdir=%{_libdir} DESTDIR=$RPM_BUILD_ROOT  mandir=%{_mandir} install
rm -f $RPM_BUILD_ROOT%{_docdir}/clisp-%{version}/doc/clisp.{dvi,1,ps}
cp -p doc/mop-spec.pdf $RPM_BUILD_ROOT%{_docdir}/clisp-%{version}/doc
%find_lang %{name}
%find_lang %{name}low
cat %{name}low.lang >> %{name}.lang


%files -f %{name}.lang
%defattr(-,root,root,-)
%{_bindir}/clisp
%{_mandir}/man1/*
%{_docdir}/clisp-%{version}
%dir %{_libdir}/clisp/base
%dir %{_libdir}/clisp/full
%dir %{_libdir}/clisp
%{_libdir}/clisp/base/lispinit.mem
%{_libdir}/clisp/base/lisp.run
%{_libdir}/clisp/full/lispinit.mem
%{_libdir}/clisp/full/lisp.run
%{_libdir}/clisp/data


%files devel
%defattr(-,root,root,-)
%attr(0755,root,root) %{_libdir}/clisp/clisp-link
%{_libdir}/clisp/base/*.a
%{_libdir}/clisp/base/*.o
%{_libdir}/clisp/base/*.h
%{_libdir}/clisp/base/*.dvi
%{_libdir}/clisp/base/makevars
%{_libdir}/clisp/full/*.a
%{_libdir}/clisp/full/*.o
%{_libdir}/clisp/full/*.h
%{_libdir}/clisp/full/*.dvi
%{_libdir}/clisp/full/makevars
%{_libdir}/clisp/linkkit


%clean
rm -fr $RPM_BUILD_ROOT


%changelog
* Wed Aug 17 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-2
- Fix libdir for x86_64

* Tue Aug 16 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-1
- New Version 2.34
