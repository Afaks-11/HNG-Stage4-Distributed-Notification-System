import * as Joi from 'joi';

export const configSchema = Joi.object({
  PORT: Joi.number().default(8080),
  NODE_ENV: Joi.string().valid('development', 'production', 'test').default('development'),
});