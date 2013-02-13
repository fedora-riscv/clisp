Name:		clisp
Summary:	ANSI Common Lisp implementation
Version:	2.49
Release:	9%{?dist}

Group:		Development/Languages
License:	GPLv2
URL:		http://www.clisp.org/
Source0:	http://downloads.sourceforge.net/clisp/clisp-%{version}.tar.bz2
# Adapt to libsvm 3.1.  Applied upstream.
Patch0:		clisp-libsvm.patch
# Fix an illegal C construct that allows GCC 4.7 to produce bad code.  Applied
# upstream.
Patch1:		clisp-hostname.patch
# Fix old ARM assembly that is invalid for newer platforms.  Sent upstream.
Patch2:		clisp-arm.patch
# Linux-specific fixes.  Sent upstream 25 Jul 2012.
Patch3:		clisp-linux.patch
BuildRequires:	compat-readline5-devel
BuildRequires:	dbus-devel
BuildRequires:	fcgi-devel
BuildRequires:	ffcall
BuildRequires:	gdbm-devel
BuildRequires:	gettext-devel
BuildRequires:	ghostscript
BuildRequires:	groff
BuildRequires:	gtk2-devel
BuildRequires:	libICE-devel
BuildRequires:	libSM-devel
BuildRequires:	libX11-devel
BuildRequires:	libXaw-devel
BuildRequires:	libXext-devel
BuildRequires:	libXft-devel
BuildRequires:	libXmu-devel
BuildRequires:	libXrender-devel
BuildRequires:	libXt-devel
BuildRequires:	libdb4-devel
BuildRequires:	libglade2-devel
BuildRequires:	libsigsegv-devel
BuildRequires:	libsvm-devel
#BuildRequires:	pari-devel
BuildRequires:	pcre-devel
BuildRequires:	postgresql-devel
BuildRequires:	zlib-devel

# See Red Hat bug #238954
ExcludeArch:	ppc64

# clisp contains a copy of gnulib, which has been granted a bundling exception:
# https://fedoraproject.org/wiki/Packaging:No_Bundled_Libraries#Packages_granted_exceptions
Provides:	bundled(gnulib)

%description
ANSI Common Lisp is a high-level, general-purpose programming
language.  GNU CLISP is a Common Lisp implementation by Bruno Haible
of Karlsruhe University and Michael Stoll of Munich University, both
in Germany.  It mostly supports the Lisp described in the ANSI Common
Lisp standard.  It runs on most Unix workstations (GNU/Linux, FreeBSD,
NetBSD, OpenBSD, Solaris, Tru64, HP-UX, BeOS, NeXTstep, IRIX, AIX and
others) and on other systems (Windows NT/2000/XP, Windows 95/98/ME)
and needs only 4 MiB of RAM.

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
Provides:	%{name}-static = %{version}-%{release} 
Requires:	%{name}%{?_isa} = %{version}-%{release}, automake

%description devel
Files necessary for linking CLISP programs.


%prep
%setup -q
%patch0
%patch1
%patch2
%patch3

# Convince CLisp to build against compat-readline5 instead of readline.
# This is to avoid pulling the GPLv3 readline 6 into a GPLv2 CLisp binary.
# See Red Hat bug #511303.
mkdir -p readline/include
ln -s %{_includedir}/readline5/readline readline/include/readline
ln -s %{_libdir}/readline5 readline/%{_lib}

# Change URLs not affected by the --hyperspec argument to configure
sed -i.orig 's|lisp.org/HyperSpec/Body/chap-7.html|lispworks.com/documentation/HyperSpec/Body/07_.htm|' \
    src/clos-package.lisp
touch -r src/clos-package.lisp.orig src/clos-package.lisp
rm -f src/clos-package.lisp.orig
for f in src/_README.*; do
  sed -i.orig 's|lisp.org/HyperSpec/FrontMatter|lispworks.com/documentation/HyperSpec/Front|' $f
  touch -r ${f}.orig $f
  rm -f ${f}.orig
done

# We only link against libraries in system directories, so we need -L dir in
# place of -Wl,-rpath -Wl,dir
cp -p src/build-aux/config.rpath config.rpath.orig
sed -i -e 's/${wl}-rpath ${wl}/-L/g' src/build-aux/config.rpath

# Enable firefox to be the default browser for displaying documentation
sed -i 's/;; \((setq \*browser\* .*)\)/\1/' src/cfgunix.lisp

%build
ulimit -s unlimited

# Do not need to specify base modules: i18n, readline, regexp, syscalls
# The dirkey module currently can only be built on Windows/Cygwin/MinGW
./configure --prefix=%{_prefix} \
	    --libdir=%{_libdir} \
	    --mandir=%{_mandir} \
	    --docdir=%{_docdir}/clisp-%{version} \
	    --fsstnd=redhat \
	    --hyperspec=http://www.lispworks.com/documentation/HyperSpec/ \
	    --with-module=berkeley-db \
	    --with-module=bindings/glibc \
	    --with-module=clx/new-clx \
	    --with-module=dbus \
	    --with-module=fastcgi \
	    --with-module=gdbm \
	    --with-module=gtk2 \
	    --with-module=libsvm \
	    --with-module=pcre \
	    --with-module=postgresql \
	    --with-module=rawsock \
	    --with-module=wildcard \
	    --with-module=zlib \
	    --with-libreadline-prefix=`pwd`/readline \
	    --cbc \
	    build \
%ifarch ppc ppc64
	    CFLAGS="${RPM_OPT_FLAGS} -DNO_GENERATIONAL_GC -DNO_MULTIMAP_FILE -DNO_SINGLEMAP -I/usr/include/readline5 -I/usr/include/libsvm -I/usr/include/libdb4 -Wa,--noexecstack -L%{_libdir}/readline5 -L%{_libdir}/libdb4" \
%else
	    CFLAGS="${RPM_OPT_FLAGS} -I/usr/include/readline5 -I/usr/include/libsvm -I/usr/include/libdb4 -Wa,--noexecstack -L%{_libdir}/readline5 -L%{_libdir}/libdb4" \
%endif
	    LDFLAGS="-L%{_libdir}/readline5 -L%{_libdir}/libdb4 -Wl,-z,noexecstack"

%install
make -C build DESTDIR=$RPM_BUILD_ROOT install
rm -f $RPM_BUILD_ROOT%{_docdir}/clisp-%{version}/doc/clisp.{dvi,1,ps}
cp -p doc/mop-spec.pdf $RPM_BUILD_ROOT%{_docdir}/clisp-%{version}/doc
cp -p doc/*.png $RPM_BUILD_ROOT%{_docdir}/clisp-%{version}/doc
cp -p doc/Why-CLISP* $RPM_BUILD_ROOT%{_docdir}/clisp-%{version}/doc
cp -p doc/regexp.html $RPM_BUILD_ROOT%{_docdir}/clisp-%{version}/doc
find $RPM_BUILD_ROOT%{_libdir} -name '*.dvi' | xargs rm -f
%find_lang %{name}
%find_lang %{name}low
cat %{name}low.lang >> %{name}.lang

# Put back the original config.rpath, and fix executable bits
cp -p config.rpath.orig $RPM_BUILD_ROOT/%{_libdir}/clisp-%{version}/build-aux/config.rpath
chmod a+x \
  $RPM_BUILD_ROOT/%{_libdir}/clisp-%{version}/build-aux/config.guess \
  $RPM_BUILD_ROOT/%{_libdir}/clisp-%{version}/build-aux/config.sub \
  $RPM_BUILD_ROOT/%{_libdir}/clisp-%{version}/build-aux/depcomp

%files -f %{name}.lang
%{_bindir}/clisp
%{_mandir}/man1/clisp.1*
%{_docdir}/clisp-%{version}
%dir %{_libdir}/clisp-%{version}/
%dir %{_libdir}/clisp-%{version}/base/
%{_libdir}/clisp-%{version}/base/lispinit.mem
%{_libdir}/clisp-%{version}/base/lisp.run
%dir %{_libdir}/clisp-%{version}/berkeley-db/
%{_libdir}/clisp-%{version}/berkeley-db/*.fas
%dir %{_libdir}/clisp-%{version}/bindings/
%dir %{_libdir}/clisp-%{version}/bindings/glibc/
%{_libdir}/clisp-%{version}/bindings/glibc/*.fas
%dir %{_libdir}/clisp-%{version}/clx/
%dir %{_libdir}/clisp-%{version}/clx/new-clx/
%{_libdir}/clisp-%{version}/clx/new-clx/*.fas
%{_libdir}/clisp-%{version}/data/
%dir %{_libdir}/clisp-%{version}/dbus/
%{_libdir}/clisp-%{version}/dbus/*.fas
%{_libdir}/clisp-%{version}/dynmod/
%dir %{_libdir}/clisp-%{version}/fastcgi/
%{_libdir}/clisp-%{version}/fastcgi/*.fas
%dir %{_libdir}/clisp-%{version}/gdbm/
%{_libdir}/clisp-%{version}/gdbm/*.fas
%dir %{_libdir}/clisp-%{version}/gtk2/
%{_libdir}/clisp-%{version}/gtk2/*.fas
%dir %{_libdir}/clisp-%{version}/libsvm/
%{_libdir}/clisp-%{version}/libsvm/*.fas
#%%dir %%{_libdir}/clisp-%%{version}/pari/
#%%{_libdir}/clisp-%%{version}/pari/*.fas
%dir %{_libdir}/clisp-%{version}/pcre/
%{_libdir}/clisp-%{version}/pcre/*.fas
%dir %{_libdir}/clisp-%{version}/postgresql/
%{_libdir}/clisp-%{version}/postgresql/*.fas
%dir %{_libdir}/clisp-%{version}/rawsock/
%{_libdir}/clisp-%{version}/rawsock/*.fas
%dir %{_libdir}/clisp-%{version}/wildcard/
%{_libdir}/clisp-%{version}/wildcard/*.fas
%dir %{_libdir}/clisp-%{version}/zlib/
%{_libdir}/clisp-%{version}/zlib/*.fas
%{_datadir}/emacs/site-lisp/*
%{_datadir}/vim/vimfiles/after/syntax/*

%files devel
%{_bindir}/clisp-link
%{_mandir}/man1/clisp-link.1*
%{_libdir}/clisp-%{version}/base/*.a
%{_libdir}/clisp-%{version}/base/*.o
%{_libdir}/clisp-%{version}/base/*.h
%{_libdir}/clisp-%{version}/base/makevars
%{_libdir}/clisp-%{version}/berkeley-db/Makefile
%{_libdir}/clisp-%{version}/berkeley-db/*.lisp
%{_libdir}/clisp-%{version}/berkeley-db/*.o
%{_libdir}/clisp-%{version}/berkeley-db/*.sh
%{_libdir}/clisp-%{version}/bindings/glibc/Makefile
%{_libdir}/clisp-%{version}/bindings/glibc/*.lisp
%{_libdir}/clisp-%{version}/bindings/glibc/*.o
%{_libdir}/clisp-%{version}/bindings/glibc/*.sh
%{_libdir}/clisp-%{version}/build-aux/
%{_libdir}/clisp-%{version}/clx/new-clx/demos/
%{_libdir}/clisp-%{version}/clx/new-clx/README
%{_libdir}/clisp-%{version}/clx/new-clx/Makefile
%{_libdir}/clisp-%{version}/clx/new-clx/*.lisp
%{_libdir}/clisp-%{version}/clx/new-clx/*.o
%{_libdir}/clisp-%{version}/clx/new-clx/*.sh
%{_libdir}/clisp-%{version}/dbus/Makefile
%{_libdir}/clisp-%{version}/dbus/*.lisp
%{_libdir}/clisp-%{version}/dbus/*.o
%{_libdir}/clisp-%{version}/dbus/*.sh
%{_libdir}/clisp-%{version}/fastcgi/README
%{_libdir}/clisp-%{version}/fastcgi/Makefile
%{_libdir}/clisp-%{version}/fastcgi/*.lisp
%{_libdir}/clisp-%{version}/fastcgi/*.o
%{_libdir}/clisp-%{version}/fastcgi/*.sh
%{_libdir}/clisp-%{version}/gdbm/Makefile
%{_libdir}/clisp-%{version}/gdbm/*.lisp
%{_libdir}/clisp-%{version}/gdbm/*.o
%{_libdir}/clisp-%{version}/gdbm/*.sh
%{_libdir}/clisp-%{version}/gtk2/Makefile
%{_libdir}/clisp-%{version}/gtk2/*.cfg
%{_libdir}/clisp-%{version}/gtk2/*.glade
%{_libdir}/clisp-%{version}/gtk2/*.lisp
%{_libdir}/clisp-%{version}/gtk2/*.o
%{_libdir}/clisp-%{version}/gtk2/*.sh
%{_libdir}/clisp-%{version}/libsvm/Makefile
%{_libdir}/clisp-%{version}/libsvm/*.lisp
%{_libdir}/clisp-%{version}/libsvm/*.o
%{_libdir}/clisp-%{version}/libsvm/*.sh
%{_libdir}/clisp-%{version}/linkkit/
#%%{_libdir}/clisp-%%{version}/pari/README
#%%{_libdir}/clisp-%%{version}/pari/Makefile
#%%{_libdir}/clisp-%%{version}/pari/*.lisp
#%%{_libdir}/clisp-%%{version}/pari/*.o
#%%{_libdir}/clisp-%%{version}/pari/*.sh
%{_libdir}/clisp-%{version}/pcre/Makefile
%{_libdir}/clisp-%{version}/pcre/*.lisp
%{_libdir}/clisp-%{version}/pcre/*.o
%{_libdir}/clisp-%{version}/pcre/*.sh
%{_libdir}/clisp-%{version}/postgresql/README
%{_libdir}/clisp-%{version}/postgresql/Makefile
%{_libdir}/clisp-%{version}/postgresql/*.lisp
%{_libdir}/clisp-%{version}/postgresql/*.o
%{_libdir}/clisp-%{version}/postgresql/*.sh
%{_libdir}/clisp-%{version}/rawsock/demos/
%{_libdir}/clisp-%{version}/rawsock/Makefile
%{_libdir}/clisp-%{version}/rawsock/*.lisp
%{_libdir}/clisp-%{version}/rawsock/*.o
%{_libdir}/clisp-%{version}/rawsock/*.sh
%{_libdir}/clisp-%{version}/wildcard/README
%{_libdir}/clisp-%{version}/wildcard/Makefile
%{_libdir}/clisp-%{version}/wildcard/*.a
%{_libdir}/clisp-%{version}/wildcard/*.lisp
%{_libdir}/clisp-%{version}/wildcard/*.o
%{_libdir}/clisp-%{version}/wildcard/*.sh
%{_libdir}/clisp-%{version}/zlib/Makefile
%{_libdir}/clisp-%{version}/zlib/*.lisp
%{_libdir}/clisp-%{version}/zlib/*.o
%{_libdir}/clisp-%{version}/zlib/*.sh
%{_datadir}/aclocal/clisp.m4


%changelog
* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 25 2012 Jerry James <loganjerry@gmail.com> - 2.49-8
- Fix build for new libdb4-devel package.
- Fix ARM assembly (bz 812928)
- Add gnulib Provides (bz 821747)
- Disable the pari module for now; it does not compile against pari 2.5

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Mar 18 2012 Daniel E. Wilson <danw@bureau-13.org> - 2.49-6
- Changed build process to define the default browser.
- Fixed module directories to move only *.fas files.
- Moved build-aux directory to the development package.
- Replaced the clisp-* wildcards with the correct version.
- More stack space may be needed on all arches (Jerry James).

* Sun Jan  8 2012 Jerry James <loganjerry@gmail.com> - 2.49-5
- Rebuild for GCC 4.7
- Minor spec file cleanups

* Thu Jun 23 2011 Jerry James <loganjerry@gmail.com> - 2.49-4
- Add libsvm patch to fix FTBFS on Rawhide (bz 715970)
- Fix readline module to also use compat-readline5 instead of readline6
- Drop unnecessary spec file elements (clean script, etc.)

* Fri Feb 11 2011 Jerry James <loganjerry@gmail.com> - 2.49-3
- Build with compat-readline5 instead of readline (#511303)
- Build the libsvm module
- Get rid of the execstack flag on Lisp images

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Nov 28 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.49-1
- clisp-2.49 (#612469)
- -devel: Provides: %%name-static (#609602)

* Sun Nov 28 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.48-2
- rebuild (libsigsegv)

* Fri Feb 26 2010 Jerry James <loganjerry@gmail.com> - 2.48-1
- new release 2.48

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.47-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.47-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 22 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.47-1
- new release 2.47

* Wed Jul  2 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.46-1
- new release 2.46

* Fri Apr 18 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.44.1-1
- new release 2.44.1

* Fri Feb 22 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.43-5
- Compile with -O0 to avoid GCC 4.3 miscompilation

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.43-4
- Autorebuild for GCC 4.3

* Sat Nov 24 2007 Gerard Milmeister <gemi@bluewin.ch> - 2.43-1
- new release 2.43

* Tue Oct 16 2007 Gerard Milmeister <gemi@bluewin.ch> - 2.42-1
- new release 2.42

* Fri May  4 2007 David Woodhouse <dwmw2@infradead.org> - 2.41-6
- Revert to overriding stack limit in specfile

* Thu May  3 2007 David Woodhouse <dwmw2@infradead.org> - 2.41-5
- Exclude ppc64 for now

* Mon Apr 30 2007 David Woodhouse <dwmw2@infradead.org> - 2.41-4
- Fix stack size in configure, restore ppc build

* Sat Dec  9 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.41-3
- rebuild without berkeley-db for now

* Fri Oct 13 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.41-1
- new version 2.41

* Tue Oct  3 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.40-3
- Added patch for x86_64

* Mon Oct  2 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.40-1
- new version 2.40

* Mon Aug 28 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.39-4
- Rebuild for FE6

* Fri Jul 28 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.39-3
- changed url to canonical web page

* Mon Jul 24 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.39-2
- rebuild with updated libsigsegv
- set CFLAGS to ""

* Mon Jul 17 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.39-1
- new version 2.39

* Fri Feb 17 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.38-2
- Rebuild for Fedora Extras 5

* Sun Jan 29 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.38-1
- new version 2.38

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
