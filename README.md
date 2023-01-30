# Key_Hunter_Max
 Search for bitcoin keys, wallet files, seed phrases in any files.
____
To start, you can use programs VS Code or PyCharm. Python must also be installed on the computer.
You can configure some options in the program.
* 1- on line 17 you can enter the number of threads. The default is 10.
* 2- in line 18 you can select the percentage of repeated characters in the key. By default, if more than 25%, the key will be thrown into the trash.
* 3- lines 20 and 21 allow you to enter the minimum and maximum number of words to search for the seed phrase.
* 4 - lines 29 and 30 are blocked by default, as they find a lot of garbage in this form. To remove the lock, remove the # character at the beginning of the line.
* 5 - line 31 searches for private keys torn and "diluted" with other characters. This is a controversial option and can be disabled. To do this, add # to the beginning of the line.
____
At the moment, the program finds keys in all common file formats, with the exception of archives. To search in the archives, they must first be unzipped.
To be sure that the search will not miss your possible keys, create test files with keys of the format you need and check them.
At the moment, work is underway to refine and optimize the program. If you come across files in which the program does not see the keys, please let me know at the email address specified in the profile. You can also write your suggestions there.
You can support me, say thank you, or make a contribution to the project by sending a transfer to the bitcoin address 17qKVuKztzRBzyDL6gFjG4qitDy2TrBFws
or ether 0x1Ec2291E33Bc399Fa65e4DE03966d5Ed7a550583
