/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


import type { Configuration } from './configuration';
import type { AxiosPromise, AxiosInstance, RawAxiosRequestConfig } from 'axios';
import globalAxios from 'axios';
// Some imports not used depending on template conditions
// @ts-ignore
import { DUMMY_BASE_URL, assertParamExists, setApiKeyToObject, setBasicAuthToObject, setBearerAuthToObject, setOAuthToObject, setSearchParams, serializeDataIfNeeded, toPathString, createRequestFunction } from './common';
import type { RequestArgs } from './base';
// @ts-ignore
import { BASE_PATH, COLLECTION_FORMATS, BaseAPI, RequiredError, operationServerMap } from './base';

/**
 * 
 * @export
 * @interface GuildDto
 */
export interface GuildDto {
    /**
     * 
     * @type {number}
     * @memberof GuildDto
     */
    'id': number;
    /**
     * 
     * @type {string}
     * @memberof GuildDto
     */
    'name': string;
}
/**
 * 
 * @export
 * @interface HTTPValidationError
 */
export interface HTTPValidationError {
    /**
     * 
     * @type {Array<ValidationError>}
     * @memberof HTTPValidationError
     */
    'detail'?: Array<ValidationError>;
}
/**
 * 
 * @export
 * @interface SoundDto
 */
export interface SoundDto {
    /**
     * 
     * @type {string}
     * @memberof SoundDto
     */
    'name': string;
    /**
     * 
     * @type {boolean}
     * @memberof SoundDto
     */
    'default': boolean;
}
/**
 * 
 * @export
 * @interface Token
 */
export interface Token {
    /**
     * 
     * @type {string}
     * @memberof Token
     */
    'access_token': string;
    /**
     * 
     * @type {string}
     * @memberof Token
     */
    'token_type': string;
}
/**
 * 
 * @export
 * @interface ValidationError
 */
export interface ValidationError {
    /**
     * 
     * @type {Array<ValidationErrorLocInner>}
     * @memberof ValidationError
     */
    'loc': Array<ValidationErrorLocInner>;
    /**
     * 
     * @type {string}
     * @memberof ValidationError
     */
    'msg': string;
    /**
     * 
     * @type {string}
     * @memberof ValidationError
     */
    'type': string;
}
/**
 * 
 * @export
 * @interface ValidationErrorLocInner
 */
export interface ValidationErrorLocInner {
}

/**
 * DefaultApi - axios parameter creator
 * @export
 */
export const DefaultApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * 
         * @summary Root
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        root: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;

            // authentication OAuth2PasswordBearer required
            // oauth required
            await setOAuthToObject(localVarHeaderParameter, "OAuth2PasswordBearer", [], configuration)


    
            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
    }
};

/**
 * DefaultApi - functional programming interface
 * @export
 */
export const DefaultApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = DefaultApiAxiosParamCreator(configuration)
    return {
        /**
         * 
         * @summary Root
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async root(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<string>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.root(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['DefaultApi.root']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
    }
};

/**
 * DefaultApi - factory interface
 * @export
 */
export const DefaultApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = DefaultApiFp(configuration)
    return {
        /**
         * 
         * @summary Root
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        root(options?: any): AxiosPromise<string> {
            return localVarFp.root(options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * DefaultApi - object-oriented interface
 * @export
 * @class DefaultApi
 * @extends {BaseAPI}
 */
export class DefaultApi extends BaseAPI {
    /**
     * 
     * @summary Root
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof DefaultApi
     */
    public root(options?: RawAxiosRequestConfig) {
        return DefaultApiFp(this.configuration).root(options).then((request) => request(this.axios, this.basePath));
    }
}



/**
 * GuildsApi - axios parameter creator
 * @export
 */
export const GuildsApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * 
         * @summary Available Guilds
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        availableGuilds: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/available-guilds`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;

            // authentication OAuth2PasswordBearer required
            // oauth required
            await setOAuthToObject(localVarHeaderParameter, "OAuth2PasswordBearer", [], configuration)


    
            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
    }
};

/**
 * GuildsApi - functional programming interface
 * @export
 */
export const GuildsApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = GuildsApiAxiosParamCreator(configuration)
    return {
        /**
         * 
         * @summary Available Guilds
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async availableGuilds(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<Array<GuildDto>>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.availableGuilds(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['GuildsApi.availableGuilds']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
    }
};

/**
 * GuildsApi - factory interface
 * @export
 */
export const GuildsApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = GuildsApiFp(configuration)
    return {
        /**
         * 
         * @summary Available Guilds
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        availableGuilds(options?: any): AxiosPromise<Array<GuildDto>> {
            return localVarFp.availableGuilds(options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * GuildsApi - object-oriented interface
 * @export
 * @class GuildsApi
 * @extends {BaseAPI}
 */
export class GuildsApi extends BaseAPI {
    /**
     * 
     * @summary Available Guilds
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof GuildsApi
     */
    public availableGuilds(options?: RawAxiosRequestConfig) {
        return GuildsApiFp(this.configuration).availableGuilds(options).then((request) => request(this.axios, this.basePath));
    }
}



/**
 * LoginApi - axios parameter creator
 * @export
 */
export const LoginApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * 
         * @summary Login
         * @param {string} discordToken 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        login: async (discordToken: string, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'discordToken' is not null or undefined
            assertParamExists('login', 'discordToken', discordToken)
            const localVarPath = `/login`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'POST', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;

            if (discordToken !== undefined) {
                localVarQueryParameter['discord_token'] = discordToken;
            }


    
            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
    }
};

/**
 * LoginApi - functional programming interface
 * @export
 */
export const LoginApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = LoginApiAxiosParamCreator(configuration)
    return {
        /**
         * 
         * @summary Login
         * @param {string} discordToken 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async login(discordToken: string, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<Token>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.login(discordToken, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['LoginApi.login']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
    }
};

/**
 * LoginApi - factory interface
 * @export
 */
export const LoginApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = LoginApiFp(configuration)
    return {
        /**
         * 
         * @summary Login
         * @param {string} discordToken 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        login(discordToken: string, options?: any): AxiosPromise<Token> {
            return localVarFp.login(discordToken, options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * LoginApi - object-oriented interface
 * @export
 * @class LoginApi
 * @extends {BaseAPI}
 */
export class LoginApi extends BaseAPI {
    /**
     * 
     * @summary Login
     * @param {string} discordToken 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof LoginApi
     */
    public login(discordToken: string, options?: RawAxiosRequestConfig) {
        return LoginApiFp(this.configuration).login(discordToken, options).then((request) => request(this.axios, this.basePath));
    }
}



/**
 * SoundsApi - axios parameter creator
 * @export
 */
export const SoundsApiAxiosParamCreator = function (configuration?: Configuration) {
    return {
        /**
         * 
         * @summary Create Sound
         * @param {string} name 
         * @param {File} file 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        createSound: async (name: string, file: File, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'name' is not null or undefined
            assertParamExists('createSound', 'name', name)
            // verify required parameter 'file' is not null or undefined
            assertParamExists('createSound', 'file', file)
            const localVarPath = `/sounds/create`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'POST', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;
            const localVarFormParams = new ((configuration && configuration.formDataCtor) || FormData)();

            if (name !== undefined) {
                localVarQueryParameter['name'] = name;
            }


            if (file !== undefined) { 
                localVarFormParams.append('file', file as any);
            }
    
    
            localVarHeaderParameter['Content-Type'] = 'multipart/form-data';
    
            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};
            localVarRequestOptions.data = localVarFormParams;

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
        /**
         * 
         * @summary Delete Sound
         * @param {string} name 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        deleteSound: async (name: string, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'name' is not null or undefined
            assertParamExists('deleteSound', 'name', name)
            const localVarPath = `/sounds/{name}`
                .replace(`{${"name"}}`, encodeURIComponent(String(name)));
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'DELETE', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;


    
            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
        /**
         * 
         * @summary Get Sound
         * @param {string} name 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getSound: async (name: string, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'name' is not null or undefined
            assertParamExists('getSound', 'name', name)
            const localVarPath = `/sounds/{name}`
                .replace(`{${"name"}}`, encodeURIComponent(String(name)));
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;


    
            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
        /**
         * 
         * @summary List Sounds
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        listSounds: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            const localVarPath = `/sounds/list`;
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;


    
            setSearchParams(localVarUrlObj, localVarQueryParameter);
            let headersFromBaseOptions = baseOptions && baseOptions.headers ? baseOptions.headers : {};
            localVarRequestOptions.headers = {...localVarHeaderParameter, ...headersFromBaseOptions, ...options.headers};

            return {
                url: toPathString(localVarUrlObj),
                options: localVarRequestOptions,
            };
        },
    }
};

/**
 * SoundsApi - functional programming interface
 * @export
 */
export const SoundsApiFp = function(configuration?: Configuration) {
    const localVarAxiosParamCreator = SoundsApiAxiosParamCreator(configuration)
    return {
        /**
         * 
         * @summary Create Sound
         * @param {string} name 
         * @param {File} file 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async createSound(name: string, file: File, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<SoundDto>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.createSound(name, file, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['SoundsApi.createSound']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Delete Sound
         * @param {string} name 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async deleteSound(name: string, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<any>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.deleteSound(name, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['SoundsApi.deleteSound']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Get Sound
         * @param {string} name 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async getSound(name: string, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<any>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.getSound(name, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['SoundsApi.getSound']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary List Sounds
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async listSounds(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<Array<SoundDto>>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.listSounds(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['SoundsApi.listSounds']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
    }
};

/**
 * SoundsApi - factory interface
 * @export
 */
export const SoundsApiFactory = function (configuration?: Configuration, basePath?: string, axios?: AxiosInstance) {
    const localVarFp = SoundsApiFp(configuration)
    return {
        /**
         * 
         * @summary Create Sound
         * @param {string} name 
         * @param {File} file 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        createSound(name: string, file: File, options?: any): AxiosPromise<SoundDto> {
            return localVarFp.createSound(name, file, options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Delete Sound
         * @param {string} name 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        deleteSound(name: string, options?: any): AxiosPromise<any> {
            return localVarFp.deleteSound(name, options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Get Sound
         * @param {string} name 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getSound(name: string, options?: any): AxiosPromise<any> {
            return localVarFp.getSound(name, options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary List Sounds
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        listSounds(options?: any): AxiosPromise<Array<SoundDto>> {
            return localVarFp.listSounds(options).then((request) => request(axios, basePath));
        },
    };
};

/**
 * SoundsApi - object-oriented interface
 * @export
 * @class SoundsApi
 * @extends {BaseAPI}
 */
export class SoundsApi extends BaseAPI {
    /**
     * 
     * @summary Create Sound
     * @param {string} name 
     * @param {File} file 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof SoundsApi
     */
    public createSound(name: string, file: File, options?: RawAxiosRequestConfig) {
        return SoundsApiFp(this.configuration).createSound(name, file, options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Delete Sound
     * @param {string} name 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof SoundsApi
     */
    public deleteSound(name: string, options?: RawAxiosRequestConfig) {
        return SoundsApiFp(this.configuration).deleteSound(name, options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Get Sound
     * @param {string} name 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof SoundsApi
     */
    public getSound(name: string, options?: RawAxiosRequestConfig) {
        return SoundsApiFp(this.configuration).getSound(name, options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary List Sounds
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof SoundsApi
     */
    public listSounds(options?: RawAxiosRequestConfig) {
        return SoundsApiFp(this.configuration).listSounds(options).then((request) => request(this.axios, this.basePath));
    }
}



