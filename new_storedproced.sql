/* stored procedures that match login + interface functionalities */

/* retrieve the name of user that logged in */
delimiter //
drop procedure if exists retrieveName //
create procedure retrieveName(IN in_email VARCHAR(25))
BEGIN
	if in_email IN (select email FROM Users) THEN
	   select first_name, last_name from Users WHERE email = in_email;
	else
		SELECT "error: that email does not exist in database" as 'Error Message';
	end if;
end;
//
delimiter ;

delimiter //
drop procedure if exists retrieveApiKey //
create procedure retrieveApiKey(IN in_email VARCHAR(25))
BEGIN
	if in_email IN (select email FROM Users) THEN
	   select api_key from Users WHERE email = in_email;
	else
		SELECT "error: that email does not exist in database" as 'Error Message';
	end if;
end;
//
delimiter ;

/* add new user information to Users table if don't already have account */
delimiter //
drop procedure if exists generateApiUser //
create procedure generateApiUser(IN first_name varchar(25), IN last_name varchar(25), IN in_email varchar(25))
BEGIN
	if in_email in (select email from Users) then
	   select 'error: this email already exists' as 'Error Message';
	else
		insert into Users(first_name, last_name, email, create_time, api_key) VALUES(first_name, last_name, in_email, CURRENT_TIME, FLOOR(RAND() * 1000000000));
	end if;
end;
//
delimiter ;

/* data for option 1: returns close values for inputted stock to graph */
delimiter //
drop procedure if exists getCloseData_ss //
create procedure getCloseData_ss(IN stock_ticker_name VARCHAR(25))
BEGIN
	if stock_ticker_name in (select stock_name from Company_Metadata) then
	   SELECT close_price from Company_Metadata as C, Daily_combined as D where C.stock_name = stock_ticker_name AND D.stock_id = C.stock_id;
	else
		select 'error: this stock does not exist in database' as 'Error Message';
	end if;
end;
//
delimiter ;

/* data for option 2: close prices for 2 stock tickers based on input names */
delimiter //
drop procedure if exists getClose_compare //
create procedure getClose_compare(IN stock_ticker_name_1 varchar(25), IN stock_ticker_name_2 varchar(25))
BEGIN
	if stock_ticker_name_1 in (select stock_name from Company_Metadata) AND stock_ticker_name_2 in (select stock_name from Company_Metadata) then
	   (select stock_id, close_price from Company_Metadata as C, Daily_combined as D
	   where C.stock_name = stock_ticker_name_1 AND D.stock_id = C.stock_id

	   UNION

	   select stock_id, close_price from Company_Metadata as C, Daily_combined as D where C.stock_name = stock_ticker_name_2 AND D.stock_id = C.stock_id);
	else
		select 'error: the stock(s) dont exist in the database' as 'Error Message';
	end if;
end;
//
delimiter ;

/* data for option 3: get close prices for all stocks within an inputted sector */
delimiter //
drop procedure if exists allClose_bySector //
create proceduer allClose_bySector(IN sector_name VARCHAR(20))
BEGIN
	if sector_name IN (select sector from Company_Metadata) then
	   select stock_id, close_price from Company_Metadata as C, Daily_combined as D
	   where C.sector = sector_name AND D.stock_id = C.stock_id
	   group by stock_id;
	else
		select 'Error: this sector is not supported' as 'Error Message';
	end if;
end;
//
delimiter ;

/* data for option 4: 10 day historical high prices for desired stock and given date */
delimiter //
drop procedure if exists tenDayHigh //
create procedure tenDayHigh(IN stock_ticker_name VARCHAR(25), IN end_date DATE)
BEGIN
	if stock_ticker_name IN (select stock_name from Company_Metadata) then
	   select high from Company_Metadata as C, Daily_combined as D
	   where C.stock_name = stock_ticker_name AND D.stock_id = C.stock_id
	   AND D.cur_date = end_date;
	else
		select 'Error: this stock not in database' as 'Error Message';
	end if;
end;
//
delimiter ;

/* data for option 5: high prices for stock with highest normalized close price for desired sector that day */
delimiter //
drop procedure if exists highPrice_normalized //
create procedure highPrice_normalized(IN sector_name varchar(20))
BEGIN
	if sector_name IN (select sector from Company_Metadata) then
	   select stock_id,high from Company_Metadata as C, Daily_combined as D
	   where C.sector = sector_name AND D.stock_id = C.stock_id
	   AND D.cur_date = CURDATE()
	   group by stock_id
	   order by normalized_close
	   having max(normalized_close);
	else
		select 'error: this sector is not supported' as 'Error Message';
	end if;
end;
//
delimiter ;
