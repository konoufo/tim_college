git checkout staging && git commit -am"committing before merging master" && (git merge master && git reset HEAD~1 */migrations/** ^
|| git reset HEAD */migrations/** && git checkout -f */migrations/**)