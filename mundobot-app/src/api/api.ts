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
         * @summary Available Guilds
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        availableGuildsAvailableGuildsGet: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
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
         * @summary Create Sound
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        createSoundSoundsCreatePost: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
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
         * @summary Delete Sound
         * @param {string} soundName 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        deleteSoundSoundsSoundNameDelete: async (soundName: string, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'soundName' is not null or undefined
            assertParamExists('deleteSoundSoundsSoundNameDelete', 'soundName', soundName)
            const localVarPath = `/sounds/{sound_name}`
                .replace(`{${"sound_name"}}`, encodeURIComponent(String(soundName)));
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
         * @param {string} soundName 
         * @param {string} guildId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getSoundSoundsSoundNameGet: async (soundName: string, guildId: string, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'soundName' is not null or undefined
            assertParamExists('getSoundSoundsSoundNameGet', 'soundName', soundName)
            // verify required parameter 'guildId' is not null or undefined
            assertParamExists('getSoundSoundsSoundNameGet', 'guildId', guildId)
            const localVarPath = `/sounds/{sound_name}`
                .replace(`{${"sound_name"}}`, encodeURIComponent(String(soundName)));
            // use dummy base URL string because the URL constructor only accepts absolute URLs.
            const localVarUrlObj = new URL(localVarPath, DUMMY_BASE_URL);
            let baseOptions;
            if (configuration) {
                baseOptions = configuration.baseOptions;
            }

            const localVarRequestOptions = { method: 'GET', ...baseOptions, ...options};
            const localVarHeaderParameter = {} as any;
            const localVarQueryParameter = {} as any;

            if (guildId !== undefined) {
                localVarQueryParameter['guild_id'] = guildId;
            }


    
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
         * @param {string} guildId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        listSoundsSoundsListGet: async (guildId: string, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'guildId' is not null or undefined
            assertParamExists('listSoundsSoundsListGet', 'guildId', guildId)
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

            if (guildId !== undefined) {
                localVarQueryParameter['guild_id'] = guildId;
            }


    
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
         * @summary Root
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        rootGet: async (options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
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
         * @summary Available Guilds
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async availableGuildsAvailableGuildsGet(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<Array<number>>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.availableGuildsAvailableGuildsGet(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['DefaultApi.availableGuildsAvailableGuildsGet']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Create Sound
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async createSoundSoundsCreatePost(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<string>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.createSoundSoundsCreatePost(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['DefaultApi.createSoundSoundsCreatePost']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Delete Sound
         * @param {string} soundName 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async deleteSoundSoundsSoundNameDelete(soundName: string, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<boolean>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.deleteSoundSoundsSoundNameDelete(soundName, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['DefaultApi.deleteSoundSoundsSoundNameDelete']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Get Sound
         * @param {string} soundName 
         * @param {string} guildId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async getSoundSoundsSoundNameGet(soundName: string, guildId: string, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<any>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.getSoundSoundsSoundNameGet(soundName, guildId, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['DefaultApi.getSoundSoundsSoundNameGet']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary List Sounds
         * @param {string} guildId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async listSoundsSoundsListGet(guildId: string, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<Array<string>>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.listSoundsSoundsListGet(guildId, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['DefaultApi.listSoundsSoundsListGet']?.[localVarOperationServerIndex]?.url;
            return (axios, basePath) => createRequestFunction(localVarAxiosArgs, globalAxios, BASE_PATH, configuration)(axios, localVarOperationServerBasePath || basePath);
        },
        /**
         * 
         * @summary Root
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        async rootGet(options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<string>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.rootGet(options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['DefaultApi.rootGet']?.[localVarOperationServerIndex]?.url;
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
         * @summary Available Guilds
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        availableGuildsAvailableGuildsGet(options?: any): AxiosPromise<Array<number>> {
            return localVarFp.availableGuildsAvailableGuildsGet(options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Create Sound
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        createSoundSoundsCreatePost(options?: any): AxiosPromise<string> {
            return localVarFp.createSoundSoundsCreatePost(options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Delete Sound
         * @param {string} soundName 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        deleteSoundSoundsSoundNameDelete(soundName: string, options?: any): AxiosPromise<boolean> {
            return localVarFp.deleteSoundSoundsSoundNameDelete(soundName, options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Get Sound
         * @param {string} soundName 
         * @param {string} guildId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        getSoundSoundsSoundNameGet(soundName: string, guildId: string, options?: any): AxiosPromise<any> {
            return localVarFp.getSoundSoundsSoundNameGet(soundName, guildId, options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary List Sounds
         * @param {string} guildId 
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        listSoundsSoundsListGet(guildId: string, options?: any): AxiosPromise<Array<string>> {
            return localVarFp.listSoundsSoundsListGet(guildId, options).then((request) => request(axios, basePath));
        },
        /**
         * 
         * @summary Root
         * @param {*} [options] Override http request option.
         * @throws {RequiredError}
         */
        rootGet(options?: any): AxiosPromise<string> {
            return localVarFp.rootGet(options).then((request) => request(axios, basePath));
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
     * @summary Available Guilds
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof DefaultApi
     */
    public availableGuildsAvailableGuildsGet(options?: RawAxiosRequestConfig) {
        return DefaultApiFp(this.configuration).availableGuildsAvailableGuildsGet(options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Create Sound
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof DefaultApi
     */
    public createSoundSoundsCreatePost(options?: RawAxiosRequestConfig) {
        return DefaultApiFp(this.configuration).createSoundSoundsCreatePost(options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Delete Sound
     * @param {string} soundName 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof DefaultApi
     */
    public deleteSoundSoundsSoundNameDelete(soundName: string, options?: RawAxiosRequestConfig) {
        return DefaultApiFp(this.configuration).deleteSoundSoundsSoundNameDelete(soundName, options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Get Sound
     * @param {string} soundName 
     * @param {string} guildId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof DefaultApi
     */
    public getSoundSoundsSoundNameGet(soundName: string, guildId: string, options?: RawAxiosRequestConfig) {
        return DefaultApiFp(this.configuration).getSoundSoundsSoundNameGet(soundName, guildId, options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary List Sounds
     * @param {string} guildId 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof DefaultApi
     */
    public listSoundsSoundsListGet(guildId: string, options?: RawAxiosRequestConfig) {
        return DefaultApiFp(this.configuration).listSoundsSoundsListGet(guildId, options).then((request) => request(this.axios, this.basePath));
    }

    /**
     * 
     * @summary Root
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     * @memberof DefaultApi
     */
    public rootGet(options?: RawAxiosRequestConfig) {
        return DefaultApiFp(this.configuration).rootGet(options).then((request) => request(this.axios, this.basePath));
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
        loginLoginPost: async (discordToken: string, options: RawAxiosRequestConfig = {}): Promise<RequestArgs> => {
            // verify required parameter 'discordToken' is not null or undefined
            assertParamExists('loginLoginPost', 'discordToken', discordToken)
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
        async loginLoginPost(discordToken: string, options?: RawAxiosRequestConfig): Promise<(axios?: AxiosInstance, basePath?: string) => AxiosPromise<Token>> {
            const localVarAxiosArgs = await localVarAxiosParamCreator.loginLoginPost(discordToken, options);
            const localVarOperationServerIndex = configuration?.serverIndex ?? 0;
            const localVarOperationServerBasePath = operationServerMap['LoginApi.loginLoginPost']?.[localVarOperationServerIndex]?.url;
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
        loginLoginPost(discordToken: string, options?: any): AxiosPromise<Token> {
            return localVarFp.loginLoginPost(discordToken, options).then((request) => request(axios, basePath));
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
    public loginLoginPost(discordToken: string, options?: RawAxiosRequestConfig) {
        return LoginApiFp(this.configuration).loginLoginPost(discordToken, options).then((request) => request(this.axios, this.basePath));
    }
}



