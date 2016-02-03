# Mercurial snapshot
%global hgver 20130208hg

Name:		clisp
Summary:	ANSI Common Lisp implementation
Version:	2.49
Release:	19.%{hgver}%{?dist}

Group:		Development/Languages
License:	GPLv2
URL:		http://www.clisp.org/
# The source for this package was pulled from upstream's mercurial repository.
# Use the following commands to generate the tarball:
#   hg clone -u 6c160a19948d \
#     http://clisp.hg.sourceforge.net:8000/hgroot/clisp/clisp clisp-2.49
#   rm -fr clisp-2.49/.hg*
#   tar cvjf clisp-2.49-20130208hg.tar.bz2 clisp-2.49
Source0:	%{name}-%{version}-%{hgver}.tar.bz2   
#Source0:	http://downloads.sourceforge.net/clisp/%%{name}-%%{version}.tar.bz2
# http://sourceforge.net/tracker/?func=detail&aid=3529607&group_id=1355&atid=301355
Patch0:		%{name}-format.patch
# http://sourceforge.net/tracker/?func=detail&aid=3529615&group_id=1355&atid=301355
Patch1:		%{name}-arm.patch
# http://sourceforge.net/tracker/?func=detail&aid=3572511&group_id=1355&atid=301355
Patch2:		%{name}-libsvm.patch
# http://sourceforge.net/tracker/?func=detail&aid=3572516&group_id=1355&atid=301355
Patch3:		%{name}-db.patch
# Linux-specific fixes.  Sent upstream 25 Jul 2012.
Patch4:		%{name}-linux.patch
# Adapt to GCC 5.x
Patch5:		%{name}-gcc5.patch
BuildRequires:	compat-readline5-devel
BuildRequires:	dbus-devel
BuildRequires:  emacs
BuildRequires:	fcgi-devel
BuildRequires:	ffcall
BuildRequires:	gdbm-devel
BuildRequires:	gettext-devel
BuildRequires:	ghostscript
BuildRequires:	groff
BuildRequires:	gtk2-devel
BuildRequires:	libXaw-devel
BuildRequires:	libXft-devel
BuildRequires:	libdb-devel
BuildRequires:	libglade2-devel
BuildRequires:	libsigsegv-devel
BuildRequires:	libsvm-devel
#BuildRequires:	pari-devel
BuildRequires:	pcre-devel
BuildRequires:	postgresql-devel
BuildRequires:	zlib-devel

# See Red Hat bugs 238954 (ppc64) and 925155 (aarch64)
ExcludeArch:	%{power64} aarch64

Requires:	emacs-filesystem
Requires:	vim-filesystem

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
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	libsigsegv-devel%{?_isa}

%description devel
Files necessary for linking CLISP programs.


%prep
%setup -q
%patch0
%patch1
%patch2
%patch3
%patch4
%patch5

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

# Fix modules that need access to symbols in libgnu.a
sed -i 's/\(${GLLIB_A}\) \(${LIBS}\)/-Wl,--whole-archive \1 -Wl,--no-whole-archive \2/' src/makemake.in

# Enable firefox to be the default browser for displaying documentation
sed -i 's/;; \((setq \*browser\* .*)\)/\1/' src/cfgunix.lisp

# Unpack the CLX manual
tar -C modules/clx -xzf modules/clx/clx-manual.tar.gz
chmod -R go+r modules/clx/clx-manual
chmod a-x modules/clx/clx-manual/html/doc-index.cgi

%build
ulimit -s unlimited

# Do not need to specify base modules: i18n, readline, regexp, syscalls.
# The dirkey module currently can only be built on Windows/Cygwin/MinGW.
# The editor module is not in good enough shape to use.
# The matlab, netica, and oracle modules require proprietary code to build.
# The pari module only works with pari 2.3.  Fedora currently has pari 2.7.
# The queens module is intended as an example only, not for actual use.
./configure --prefix=%{_prefix} \
	    --libdir=%{_libdir} \
	    --mandir=%{_mandir} \
	    --infodir=%{_infodir} \
	    --docdir=%{_pkgdocdir} \
	    --fsstnd=redhat \
	    --hyperspec=http://www.lispworks.com/documentation/HyperSpec/ \
	    --with-module=asdf \
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
	    --with-module=zlib \
	    --with-libreadline-prefix=$PWD/readline \
	    --cbc \
	    build \
%ifarch ppc %{power64}
	    CPPFLAGS="-DNO_GENERATIONAL_GC -DNO_MULTIMAP_FILE -DNO_SINGLEMAP -I/usr/include/readline5 -I/usr/include/libsvm" \
%else
	    CPPFLAGS="-I/usr/include/readline5 -I/usr/include/libsvm" \
%endif
	    CFLAGS="%{optflags} -Wa,--noexecstack -L%{_libdir}/readline5" \
	    LDFLAGS="-Wl,-z,relro -L%{_libdir}/readline5 -Wl,-z,noexecstack"

%install
ulimit -s unlimited
make -C build DESTDIR=%{buildroot} install
cp -a build/full %{buildroot}%{_libdir}/%{name}-%{version}+
rm -f %{buildroot}%{_pkgdocdir}/doc/clisp.{dvi,1,ps}
rm -f %{buildroot}%{_pkgdocdir}/{COPYRIGHT,GNU-GPL}
cp -p doc/mop-spec.pdf %{buildroot}%{_pkgdocdir}/doc
cp -p doc/*.png %{buildroot}%{_pkgdocdir}/doc
cp -p doc/Why-CLISP* %{buildroot}%{_pkgdocdir}/doc
cp -p doc/regexp.html %{buildroot}%{_pkgdocdir}/doc
find %{buildroot}%{_libdir} -name '*.dvi' | xargs rm -f
%find_lang %{name}
%find_lang %{name}low
cat %{name}low.lang >> %{name}.lang

# Compile the Emacs interface
pushd %{buildroot}%{_datadir}/emacs/site-lisp
%{_emacs_bytecompile} *.el
popd

# Put back the original config.rpath, and fix executable bits
cp -p config.rpath.orig %{buildroot}/%{_libdir}/%{name}-%{version}+/build-aux/config.rpath
chmod a+x \
  %{buildroot}/%{_libdir}/%{name}-%{version}+/build-aux/config.guess \
  %{buildroot}/%{_libdir}/%{name}-%{version}+/build-aux/config.sub \
  %{buildroot}/%{_libdir}/%{name}-%{version}+/build-aux/depcomp \
  %{buildroot}/%{_libdir}/%{name}-%{version}+/build-aux/install-sh \

# Fix paths in the Makefiles
for mk in $(find %{buildroot}%{_libdir} -name Makefile); do
  sed -e "s,$PWD/modules,%{_libdir}/%{name}-%{version}+," \
      -e "s,$PWD/build/clisp,%{_bindir}/clisp," \
      -e "s,$PWD/build/linkkit,%{_libdir}/%{name}-%{version}+/linkkit," \
      -i $mk
done
for mk in %{buildroot}%{_libdir}/%{name}-%{version}+/{base,full}/makevars; do
  sed -e "s, -I$PWD[^']*,," \
      -e "s,$PWD/readline.*readline/lib[[:digit:]]*,-L%{_libdir}/readline5 -lreadline," \
      -e "s,%{_libdir}/lib\([[:alnum:]]*\)\.so,-l\1,g" \
      -i $mk
done

# Install config.h, which is needed in some cases
for dir in %{buildroot}%{_libdir}/%{name}-%{version}+/*; do
  cp -p build/$(basename $dir)/config.h $dir || :
done
cp -p build/config.h %{buildroot}%{_libdir}/%{name}-%{version}+
cp -p build/clx/new-clx/config.h \
   %{buildroot}%{_libdir}/%{name}-%{version}+/clx/new-clx

# Fix permissions
chmod 0755 %{buildroot}%{_bindir}/%{name}
chmod 0755 %{buildroot}%{_libdir}/%{name}-%{version}+/full/lisp.run

# Fix broken symlinks in the full set
pushd %{buildroot}%{_libdir}/%{name}-%{version}+/full
for obj in bogomips calls gettext readline regexi; do
  rm -f ${obj}.o
  ln -s ../base/${obj}.o ${obj}.o
done
for obj in libgnu libnoreadline lisp; do
  rm -f ${obj}.a
  ln -s ../base/${obj}.a ${obj}.a
done
for obj in fastcgi fastcgi_wrappers; do
  rm -f ${obj}.o
  ln -s ../fastcgi/${obj}.o ${obj}.o
done
rm -f bdb.o
ln -s ../berkeley-db/bdb.o bdb.o
rm -f clx.o
ln -s ../clx/new-clx/clx.o clx.o
rm -f cpcre.o
ln -s ../pcre/cpcre.o cpcre.o
rm -f dbus.o
ln -s ../dbus/dbus.o dbus.o
rm -f gdbm.o
ln -s ../gdbm/gdbm.o gdbm.o
rm -f gtk.o
ln -s ../gtk2/gtk.o gtk.o
rm -f libsvm.o
ln -s ../libsvm/libsvm.o libsvm.o
rm -f linux.o
ln -s ../bindings/glibc/linux.o linux.o
rm -f postgresql.o
ln -s ../postgresql/postgresql.o postgresql.o
rm -f rawsock.o
ln -s ../rawsock/rawsock.o rawsock.o
rm -f zlib.o
ln -s ../zlib/zlib.o zlib.o
popd

# Help the debuginfo generator
ln -s ../../src/modules.c build/base/modules.c
ln -s ../../src/modules.c build/full/modules.c

%files -f %{name}.lang
%license COPYRIGHT GNU-GPL
%{_bindir}/clisp
%{_mandir}/man1/clisp.1*
%{_pkgdocdir}/
%dir %{_libdir}/%{name}-%{version}+/
%dir %{_libdir}/%{name}-%{version}+/asdf/
%{_libdir}/%{name}-%{version}+/asdf/asdf.fas
%dir %{_libdir}/%{name}-%{version}+/base/
%{_libdir}/%{name}-%{version}+/base/lispinit.mem
%{_libdir}/%{name}-%{version}+/base/lisp.run
%dir %{_libdir}/%{name}-%{version}+/berkeley-db/
%{_libdir}/%{name}-%{version}+/berkeley-db/*.fas
%dir %{_libdir}/%{name}-%{version}+/bindings/
%dir %{_libdir}/%{name}-%{version}+/bindings/glibc/
%{_libdir}/%{name}-%{version}+/bindings/glibc/*.fas
%dir %{_libdir}/%{name}-%{version}+/clx/
%dir %{_libdir}/%{name}-%{version}+/clx/new-clx/
%{_libdir}/%{name}-%{version}+/clx/new-clx/*.fas
%{_libdir}/%{name}-%{version}+/data/
%dir %{_libdir}/%{name}-%{version}+/dbus/
%{_libdir}/%{name}-%{version}+/dbus/*.fas
%{_libdir}/%{name}-%{version}+/dynmod/
%dir %{_libdir}/%{name}-%{version}+/fastcgi/
%{_libdir}/%{name}-%{version}+/fastcgi/*.fas
%dir %{_libdir}/%{name}-%{version}+/full/
%{_libdir}/%{name}-%{version}+/full/lispinit.mem
%{_libdir}/%{name}-%{version}+/full/lisp.run
%dir %{_libdir}/%{name}-%{version}+/gdbm/
%{_libdir}/%{name}-%{version}+/gdbm/*.fas
%dir %{_libdir}/%{name}-%{version}+/gtk2/
%{_libdir}/%{name}-%{version}+/gtk2/*.fas
%dir %{_libdir}/%{name}-%{version}+/libsvm/
%{_libdir}/%{name}-%{version}+/libsvm/*.fas
#%%dir %%{_libdir}/%%{name}-%%{version}/pari/
#%%{_libdir}/%%{name}-%%{version}/pari/*.fas
%dir %{_libdir}/%{name}-%{version}+/pcre/
%{_libdir}/%{name}-%{version}+/pcre/*.fas
%dir %{_libdir}/%{name}-%{version}+/postgresql/
%{_libdir}/%{name}-%{version}+/postgresql/*.fas
%dir %{_libdir}/%{name}-%{version}+/rawsock/
%{_libdir}/%{name}-%{version}+/rawsock/*.fas
%dir %{_libdir}/%{name}-%{version}+/zlib/
%{_libdir}/%{name}-%{version}+/zlib/*.fas
%{_datadir}/emacs/site-lisp/*
%{_datadir}/vim/vimfiles/after/syntax/*

%files devel
%doc modules/clx/clx-manual
%{_bindir}/clisp-link
%{_mandir}/man1/clisp-link.1*
%{_libdir}/%{name}-%{version}+/asdf/Makefile
%{_libdir}/%{name}-%{version}+/asdf/*.lisp
%{_libdir}/%{name}-%{version}+/asdf/*.sh
%{_libdir}/%{name}-%{version}+/base/*.a
%{_libdir}/%{name}-%{version}+/base/*.h
%{_libdir}/%{name}-%{version}+/base/*.o
%{_libdir}/%{name}-%{version}+/base/makevars
%{_libdir}/%{name}-%{version}+/berkeley-db/Makefile
%{_libdir}/%{name}-%{version}+/berkeley-db/*.h
%{_libdir}/%{name}-%{version}+/berkeley-db/*.lisp
%{_libdir}/%{name}-%{version}+/berkeley-db/*.o
%{_libdir}/%{name}-%{version}+/berkeley-db/*.sh
%{_libdir}/%{name}-%{version}+/bindings/glibc/Makefile
%{_libdir}/%{name}-%{version}+/bindings/glibc/*.lisp
%{_libdir}/%{name}-%{version}+/bindings/glibc/*.o
%{_libdir}/%{name}-%{version}+/bindings/glibc/*.sh
%{_libdir}/%{name}-%{version}+/build-aux/
%{_libdir}/%{name}-%{version}+/clx/new-clx/demos/
%{_libdir}/%{name}-%{version}+/clx/new-clx/README
%{_libdir}/%{name}-%{version}+/clx/new-clx/Makefile
%{_libdir}/%{name}-%{version}+/clx/new-clx/*.h
%{_libdir}/%{name}-%{version}+/clx/new-clx/*.lisp
%{_libdir}/%{name}-%{version}+/clx/new-clx/*.o
%{_libdir}/%{name}-%{version}+/clx/new-clx/*.sh
%{_libdir}/%{name}-%{version}+/config.h
%{_libdir}/%{name}-%{version}+/dbus/Makefile
%{_libdir}/%{name}-%{version}+/dbus/*.h
%{_libdir}/%{name}-%{version}+/dbus/*.lisp
%{_libdir}/%{name}-%{version}+/dbus/*.o
%{_libdir}/%{name}-%{version}+/dbus/*.sh
%{_libdir}/%{name}-%{version}+/fastcgi/README
%{_libdir}/%{name}-%{version}+/fastcgi/Makefile
%{_libdir}/%{name}-%{version}+/fastcgi/*.h
%{_libdir}/%{name}-%{version}+/fastcgi/*.lisp
%{_libdir}/%{name}-%{version}+/fastcgi/*.o
%{_libdir}/%{name}-%{version}+/fastcgi/*.sh
%{_libdir}/%{name}-%{version}+/full/*.a
%{_libdir}/%{name}-%{version}+/full/*.h
%{_libdir}/%{name}-%{version}+/full/*.o
%{_libdir}/%{name}-%{version}+/full/makevars
%{_libdir}/%{name}-%{version}+/gdbm/Makefile
%{_libdir}/%{name}-%{version}+/gdbm/*.h
%{_libdir}/%{name}-%{version}+/gdbm/*.lisp
%{_libdir}/%{name}-%{version}+/gdbm/*.o
%{_libdir}/%{name}-%{version}+/gdbm/*.sh
%{_libdir}/%{name}-%{version}+/gtk2/Makefile
%{_libdir}/%{name}-%{version}+/gtk2/*.cfg
%{_libdir}/%{name}-%{version}+/gtk2/*.glade
%{_libdir}/%{name}-%{version}+/gtk2/*.h
%{_libdir}/%{name}-%{version}+/gtk2/*.lisp
%{_libdir}/%{name}-%{version}+/gtk2/*.o
%{_libdir}/%{name}-%{version}+/gtk2/*.sh
%{_libdir}/%{name}-%{version}+/libsvm/README
%{_libdir}/%{name}-%{version}+/libsvm/Makefile
%{_libdir}/%{name}-%{version}+/libsvm/*.h
%{_libdir}/%{name}-%{version}+/libsvm/*.lisp
%{_libdir}/%{name}-%{version}+/libsvm/*.o
%{_libdir}/%{name}-%{version}+/libsvm/*.sh
%{_libdir}/%{name}-%{version}+/linkkit/
#%%{_libdir}/%%{name}-%%{version}/pari/README
#%%{_libdir}/%%{name}-%%{version}/pari/Makefile
#%%{_libdir}/%%{name}-%%{version}/pari/*.h
#%%{_libdir}/%%{name}-%%{version}/pari/*.lisp
#%%{_libdir}/%%{name}-%%{version}/pari/*.o
#%%{_libdir}/%%{name}-%%{version}/pari/*.sh
%{_libdir}/%{name}-%{version}+/pcre/Makefile
%{_libdir}/%{name}-%{version}+/pcre/*.h
%{_libdir}/%{name}-%{version}+/pcre/*.lisp
%{_libdir}/%{name}-%{version}+/pcre/*.o
%{_libdir}/%{name}-%{version}+/pcre/*.sh
%{_libdir}/%{name}-%{version}+/postgresql/README
%{_libdir}/%{name}-%{version}+/postgresql/Makefile
%{_libdir}/%{name}-%{version}+/postgresql/*.h
%{_libdir}/%{name}-%{version}+/postgresql/*.lisp
%{_libdir}/%{name}-%{version}+/postgresql/*.o
%{_libdir}/%{name}-%{version}+/postgresql/*.sh
%{_libdir}/%{name}-%{version}+/rawsock/demos/
%{_libdir}/%{name}-%{version}+/rawsock/Makefile
%{_libdir}/%{name}-%{version}+/rawsock/*.h
%{_libdir}/%{name}-%{version}+/rawsock/*.lisp
%{_libdir}/%{name}-%{version}+/rawsock/*.o
%{_libdir}/%{name}-%{version}+/rawsock/*.sh
%{_libdir}/%{name}-%{version}+/zlib/Makefile
%{_libdir}/%{name}-%{version}+/zlib/*.h
%{_libdir}/%{name}-%{version}+/zlib/*.lisp
%{_libdir}/%{name}-%{version}+/zlib/*.o
%{_libdir}/%{name}-%{version}+/zlib/*.sh
%{_datadir}/aclocal/clisp.m4


%changelog
* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.49-19.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Sep 29 2015 Jerry James <loganjerry@gmail.com> - 2.49-18.20130208hg
- Install the full link set
- Fix installed Makefile paths
- Fix clx manual permissions

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-17.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Apr  3 2015 Jerry James <loganjerry@gmail.com> - 2.49-16.20130208hg
- Fix modules that need access to symbols in libgnu.a

* Wed Feb 11 2015 Jerry James <loganjerry@gmail.com> - 2.49-15.20130208hg
- Add -gcc5 patch to fix 32-bit build with gcc 5.0
- Use license macro

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-14.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-13.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Aug 30 2013 Jerry James <loganjerry@gmail.com> - 2.49-11.20130208hg
- clisp does not support aarch64 (bz 925155)
- Adapt to versionless docdir (bz 992605 and 993701)
- More stack space needed to install

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-11.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 2.49-10.20130208hg
- Perl 5.18 rebuild

* Mon Feb 18 2013 Jerry James <loganjerry@gmail.com> - 2.49-9.20130208hg
- Update to mercurial snapshot to fix FTBFS
- Drop upstreamed -hostname patch
- Build against libdb instead of libdb4
- Include the CLX manual in the -devel documentation
- Compile the Emacs Lisp interface
- Build the asdf module

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
