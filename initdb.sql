DROP TABLE IF EXISTS features;
CREATE TABLE public.features (
	user_id int PRIMARY KEY, 
	total_experiments INT NOT NULL, 
	average_experiment_time NUMERIC NOT NULL, 
	most_commonly_used_compounds VARCHAR(15) [], 
	UNIQUE(user_id)
);

SELECT * FROM public.features;