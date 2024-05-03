#!/bin/bash
#shellcheck disable=SC2002

DEPENDS=(
	'mpv'
	'python-colorama'
	'python-gradio-client'
	'python-gtts'
	'python-huggingface-hub'
	'python-mpv'
	'python-openai'
	'python-pydub'
	'python-pygame'
	'python-termcolor'
	'qview'
)

install_pkg(){
	case $1 in
		'apt') dpkg -l "$2" 2>'/dev/null' || sudo apt install -y "$2" 2>'/dev/null';;
		'yum') yum list installed "$2" 2>'/dev/null' || sudo yum install -y "$2" 2>'/dev/null';;
		'dnf') dnf list installed "$2" 2>'/dev/null' || sudo dnf install -y "$2" 2>'/dev/null';;
		'pacman')
			if ! pacman -Q "$2" 2>'/dev/null'; then
				sudo pacman -S --noconfirm "$2" 2>'/dev/null'
				if ! pacman -Q "$2" 2>'/dev/null'; then
					yay -S --noconfirm "$2" 2>'/dev/null'
				fi
			fi;;
	esac
}

# A redundant file chmodder

#for FL in "${OBJECTS[@]}"; do
#	if [[ -e "$FL" && ! -x "$FL" ]]; then
#		echo -e "making $FL executable\n"
#		sudo chmod +x "$FL"
#	fi
#done

[ ! -x 'gh0sty' ] && chmod +x 'gh0sty'
[ ! -x 'gh0sty.py' ] && chmod +x 'gh0sty.py'
[ -e '/bin/gh0sty' ] && sudo rm '/bin/gh0sty'
[ -d '/usr/share/Gh0sty' ] && sudo rm -r '/usr/share/Gh0sty'
[ -d '__pycache__/' ] && rm -r '__pycache__/' 2>'/dev/null'

if [ $# -eq 0 ]; then
	if command -v apt >'/dev/null'; then PKGMGR='apt'
	elif command -v yum >'/dev/null'; then PKGMGR='yum'
	elif command -v dnf >'/dev/null'; then PKGMGR='dnf'
	elif command -v pacman >'/dev/null'; then PKGMGR='pacman'
	else echo '⚠ unknown package manager ⚠' & exit 1
	fi
	for PKG in "${DEPENDS[@]}"; do
		install_pkg "$PKGMGR" "$PKG"
	done

# Uncomment below section if none of the above package managers
# are installed on the machine, or there are problems with
# missing packages in their repositories, be sure that either
# pip, pipx or pip3 are installed, there are known issues with
# pipx for installing packages directly into the system

	if command -v pip >'/dev/null'; then
		pip install -q --no-color -r 'requirements.txt'
	else echo '⚠ pip not installed ⚠'
	fi
#	if command -v pip3 >'/dev/null'; then
#		pip3 install -q 'requirements.txt'
#	else echo '⚠ pip3 not installed ⚠'
#	fi
#	if command -v pipx >'/dev/null'; then
#		cat 'requirements.txt' | xargs -n 1 pipx install
#	else echo '⚠ pipx not installed ⚠'
#	fi

	sudo cp -r '../Gh0sty/' '/usr/share/'
	sudo cp 'gh0sty' '/bin'
	cp 'gh0sty' "$HOME/.local/bin"
elif [[ "$1" =~ ^(--remove|-r|r)$ ]]; then
	[ -d '/usr/share/Gh0sty' ] && sudo rm -r '/usr/share/Gh0sty'
	[ -e '/bin/gh0sty' ] && sudo rm '/bin/gh0sty'
	[ -e "$HOME/.local/bin/gh0sty" ] && sudo rm "$HOME/.local/bin/gh0sty"
fi && ./'commit.sh' 2>'/dev/null'

unset DEPENDS
