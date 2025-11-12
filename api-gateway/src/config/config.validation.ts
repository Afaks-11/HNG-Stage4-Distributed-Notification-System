import * as Joi from 'joi';

export const configSchema = Joi.object({
  PORT: Joi.number().default(3000),
  JWT_SECRET: Joi.string().required(),
  STATUS_DB_URL: Joi.string().uri().required(),
  REDIS_URL: Joi.string().uri().required(),
  RABBITMQ_URL: Joi.string().uri().required(),
});
