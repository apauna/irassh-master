USE irassh;

ALTER TABLE `downloads` ADD `shasum` VARCHAR(64) DEFAULT NULL;
