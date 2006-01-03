Name:		clisp
Summary:	Common Lisp (ANSI CL) implementation
Version:	2.37
Release: 	2%{?dist}

Group:		Development/Languages
License:	GPL
URL:		http://sourceforge.net/projects/clisp
Source:		http://download.sourceforge.net/clisp/clisp-2.36.tar.bz2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	readline-devel, gettext, pcre-devel, postgresql-devel
BuildRequires:	libsigsegv-devel, db4-devel, zlib-devel
BuildRequires:  libICE-devel
BuildRequires:  libSM-devel
BuildRequires:  libX11-devel
BuildRequires:  libXaw-devel
BuildRequires:  libXext-devel
BuildRequires:  libXft-devel
BuildRequires:  libXmu-devel
BuildRequires:  libXrender-devel
BuildRequires:  libXt-devel
BuildRequires:	imake
ExcludeArch:	ppc ppc64


%description
ANSI Common Lisp is a high-level, general-purpose programming
language.  GNU CLISP is a Common Lisp implementation by Bruno Haible
of Karlsruhe University and Michael Stoll of Munich University, both
in Germany.  It mostly supports the Lisp described in the ANSI Common
Lisp standard.  It runs on most Unix workstations (GNU/Linux, FreeBSD,
NetBSD, OpenBSD, Solaris, Tru64, HP-UX, BeOS, NeXTstep, IRIX, AIX and
others) and on other systems (Windows NT/2000/XP, Windows 95/98/ME)
and needs only 4 MB of RAM.

It is Free Software and may be distributed under the terms of GNU GPL,
while it is possible to distribute commercial proprietary applications
compiled with GNU CLISP.

The user interface comes in English, German, French, Spanish, Dutch,
Russian and Danish, and can be changed at run time.  GNU CLISP
includes an interpreter, a compiler, a debugger, CLOS, MOP, a foreign
language interface, sockets, i18n, fast bignums and more.  An X11
interface is available through CLX, Garnet, CLUE/CLIO.  GNU CLISP runs
Maxima, ACL2 and many other Common Lisp packages.


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
# setting CFLAGS breaks the build
./configure --prefix=%{_prefix} \
	    --libdir=%{_libdir} \
	    --fsstnd=redhat \
	    --with-dynamic-ffi \
	    --with-module=berkeley-db \
	    --with-module=clx/new-clx \
	    --with-module=pcre \
	    --with-module=postgresql \
	    --with-module=rawsock \
	    --with-module=wildcard \
	    --with-module=zlib \
   	    --with-module=bindings/glibc \
	    --with-readline \
	    --build build


%install
rm -rf $RPM_BUILD_ROOT
make -C build prefix=%{_prefix} libdir=%{_libdir} mandir=%{_mandir} DESTDIR=$RPM_BUILD_ROOT install
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
* Tue Jan  3 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.37-1
- new version 2.37

* Wed Dec 28 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.36-1
- New Version 2.36

* Tue Aug 30 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.35-1
- New Version 2.35

* Thu Aug 18 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-5
- do the compilation in the "build" directory

* Thu Aug 18 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-4
- Use ulimit for the build to succeed on ppc

* Wed Aug 17 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-3
- Build fails on ppc, exclude for now

* Wed Aug 17 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-2
- Fix libdir for x86_64

* Tue Aug 16 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-1
- New Version 2.34
